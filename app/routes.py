# app/routes.py
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app, abort
)
from flask_login import login_required, current_user
from . import db
from .models import Venue, Event, Resource, Participant
from .utils import require_roles
from datetime import datetime

main_bp = Blueprint('main', __name__)

# ---------- helpers ----------
def is_conflict(venue_id, date, start, end, ignore_id=None):
    events = Event.query.filter_by(venue_id=venue_id, date=date).all()
    for e in events:
        if ignore_id and e.id == ignore_id:
            continue
        if start < e.end_time and end > e.start_time:
            return True
    return False

def flash_form_errors(form):
    messages = []
    for field, errs in form.errors.items():
        for e in errs:
            messages.append(f"{field}: {e}")
    if messages:
        flash("Please fix the form errors and try again.", "danger")
        current_app.logger.debug("Form errors: %s", messages)

# ---------- root ----------
@main_bp.route('/')
def index():
    return redirect(url_for('main.list_events'))

# ---------- venues ----------
@main_bp.route('/venues')
def list_venues():
    venues = Venue.query.order_by(Venue.name).all()
    return render_template('venues/list.html', venues=venues)

@main_bp.route('/venue/add', methods=['GET','POST'])
@login_required
@require_roles('admin')  # only admin can manage venues (change if you want staff too)
def add_venue():
    from .forms import VenueForm
    form = VenueForm()
    if form.validate_on_submit():
        v = Venue(name=form.name.data.strip(), capacity=form.capacity.data)
        db.session.add(v)
        db.session.commit()
        flash("Venue added", "success")
        return redirect(url_for('main.list_venues'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('venues/add_edit.html', form=form, action="Add")

@main_bp.route('/venue/<int:venue_id>/edit', methods=['GET','POST'])
@login_required
@require_roles('admin')
def edit_venue(venue_id):
    v = Venue.query.get_or_404(venue_id)
    from .forms import VenueForm
    form = VenueForm(obj=v)
    if form.validate_on_submit():
        v.name = form.name.data.strip()
        v.capacity = form.capacity.data
        db.session.commit()
        flash("Venue updated", "success")
        return redirect(url_for('main.list_venues'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('venues/add_edit.html', form=form, action="Edit")

@main_bp.route('/venue/<int:venue_id>/delete', methods=['POST'])
@login_required
@require_roles('admin')
def delete_venue(venue_id):
    v = Venue.query.get_or_404(venue_id)
    if v.events:
        flash("Cannot delete venue with existing events. Delete its events first.", "danger")
        return redirect(url_for('main.list_venues'))
    db.session.delete(v)
    db.session.commit()
    flash("Venue deleted.", "info")
    return redirect(url_for('main.list_venues'))

# ---------- resources ----------
@main_bp.route('/venue/<int:venue_id>/resources')
@login_required
def manage_resources(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    return render_template('venues/resources.html', venue=venue)

@main_bp.route('/venue/<int:venue_id>/resource/add', methods=['GET','POST'])
@login_required
@require_roles('admin')
def add_resource(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    from .forms import ResourceForm
    form = ResourceForm()
    if form.validate_on_submit():
        res = Resource(name=form.name.data.strip(), quantity=form.quantity.data, venue_id=venue_id)
        db.session.add(res)
        db.session.commit()
        flash("Resource added", "success")
        return redirect(url_for('main.manage_resources', venue_id=venue_id))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('venues/resource_add_edit.html', form=form, action="Add", venue=venue)

@main_bp.route('/resource/<int:res_id>/edit', methods=['GET','POST'])
@login_required
@require_roles('admin')
def edit_resource(res_id):
    res = Resource.query.get_or_404(res_id)
    from .forms import ResourceForm
    form = ResourceForm(obj=res)
    if form.validate_on_submit():
        res.name = form.name.data.strip()
        res.quantity = form.quantity.data
        db.session.commit()
        flash("Resource updated", "success")
        return redirect(url_for('main.manage_resources', venue_id=res.venue_id))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('venues/resource_add_edit.html', form=form, action="Edit", venue=res.venue)

@main_bp.route('/resource/<int:res_id>/delete', methods=['POST'])
@login_required
@require_roles('admin')
def delete_resource(res_id):
    res = Resource.query.get_or_404(res_id)
    venue_id = res.venue_id
    db.session.delete(res)
    db.session.commit()
    flash("Resource deleted", "info")
    return redirect(url_for('main.manage_resources', venue_id=venue_id))

# ---------- events ----------
@main_bp.route('/events')
def list_events():
    q_date = request.args.get('date')
    if q_date:
        try:
            dt = datetime.strptime(q_date, '%Y-%m-%d').date()
            events = Event.query.filter_by(date=dt).order_by(Event.start_time).all()
        except Exception:
            events = Event.query.order_by(Event.date, Event.start_time).all()
    else:
        events = Event.query.order_by(Event.date, Event.start_time).all()
    return render_template('events/list.html', events=events)

@main_bp.route('/event/add', methods=['GET','POST'])
@login_required
@require_roles('admin', 'staff')
def add_event():
    from .forms import EventForm
    form = EventForm()
    form.venue_id.choices = [(v.id, v.name) for v in Venue.query.order_by(Venue.name).all()]
    if form.validate_on_submit():
        if form.start_time.data >= form.end_time.data:
            flash('Start time must be before end time.', 'danger')
            return render_template('events/add_edit.html', form=form, action='Add')
        if is_conflict(form.venue_id.data, form.date.data, form.start_time.data, form.end_time.data):
            flash('Venue is already booked for that time.', 'danger')
            return render_template('events/add_edit.html', form=form, action='Add')
        e = Event(
            title=form.title.data.strip(),
            description=form.description.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            venue_id=form.venue_id.data
        )
        db.session.add(e)
        db.session.commit()
        flash('Event added.', 'success')
        return redirect(url_for('main.list_events'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('events/add_edit.html', form=form, action="Add")

@main_bp.route('/event/<int:event_id>/edit', methods=['GET','POST'])
@login_required
@require_roles('admin', 'staff')
def edit_event(event_id):
    e = Event.query.get_or_404(event_id)
    from .forms import EventForm
    form = EventForm(obj=e)
    form.venue_id.choices = [(v.id, v.name) for v in Venue.query.order_by(Venue.name).all()]
    if form.validate_on_submit():
        if form.start_time.data >= form.end_time.data:
            flash('Start time must be before end time.', 'danger')
            return render_template('events/add_edit.html', form=form, action='Edit')
        if is_conflict(form.venue_id.data, form.date.data, form.start_time.data, form.end_time.data, ignore_id=e.id):
            flash('Venue conflict for chosen time.', 'danger')
            return render_template('events/add_edit.html', form=form, action='Edit')
        e.title = form.title.data.strip()
        e.description = form.description.data
        e.date = form.date.data
        e.start_time = form.start_time.data
        e.end_time = form.end_time.data
        e.venue_id = form.venue_id.data
        db.session.commit()
        flash('Event updated', 'success')
        return redirect(url_for('main.list_events'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('events/add_edit.html', form=form, action="Edit")

@main_bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
@require_roles('admin')
def delete_event(event_id):
    e = Event.query.get_or_404(event_id)
    db.session.delete(e)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('main.list_events'))

# ---------- participants ----------
@main_bp.route('/participants')
@login_required
def list_participants():
    participants = Participant.query.order_by(Participant.name).all()
    return render_template('participants/list.html', participants=participants)

@main_bp.route('/participant/add', methods=['GET','POST'])
@login_required
@require_roles('admin', 'staff')
def add_participant():
    from .forms import ParticipantForm
    form = ParticipantForm()
    if form.validate_on_submit():
        p = Participant(
            name=form.name.data.strip(),
            email=form.email.data.strip() if form.email.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
            notes=form.notes.data
        )
        db.session.add(p)
        db.session.commit()
        flash("Participant added", "success")
        return redirect(url_for('main.list_participants'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('participants/add_edit.html', form=form, action="Add")

@main_bp.route('/participant/<int:pid>/edit', methods=['GET','POST'])
@login_required
@require_roles('admin', 'staff')
def edit_participant(pid):
    p = Participant.query.get_or_404(pid)
    from .forms import ParticipantForm
    form = ParticipantForm(obj=p)
    if form.validate_on_submit():
        p.name = form.name.data.strip()
        p.email = form.email.data.strip() if form.email.data else None
        p.phone = form.phone.data.strip() if form.phone.data else None
        p.notes = form.notes.data
        db.session.commit()
        flash("Participant updated", "success")
        return redirect(url_for('main.list_participants'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('participants/add_edit.html', form=form, action="Edit")

@main_bp.route('/participant/<int:pid>/delete', methods=['POST'])
@login_required
@require_roles('admin')
def delete_participant(pid):
    p = Participant.query.get_or_404(pid)
    p.events = []
    db.session.delete(p)
    db.session.commit()
    flash("Participant deleted", "info")
    return redirect(url_for('main.list_participants'))

# ---------- event <-> participants ----------
@main_bp.route('/event/<int:event_id>/participants')
@login_required
def event_participants_view(event_id):
    event = Event.query.get_or_404(event_id)
    available = Participant.query.filter(~Participant.events.any(id=event.id)).order_by(Participant.name).all()
    return render_template('events/participants.html', event=event, available=available)

@main_bp.route('/event/<int:event_id>/participant/add', methods=['POST'])
@login_required
@require_roles('admin', 'staff')
def add_participant_to_event(event_id):
    event = Event.query.get_or_404(event_id)
    pid = request.form.get('participant_id')
    if not pid:
        flash("No participant selected", "danger")
        return redirect(url_for('main.event_participants_view', event_id=event_id))
    p = Participant.query.get_or_404(int(pid))
    if p in event.participants:
        flash("Participant already registered for this event", "warning")
    else:
        if event.venue and event.venue.capacity and len(event.participants) >= event.venue.capacity:
            flash("Cannot add participant — venue capacity reached.", "danger")
        else:
            event.participants.append(p)
            db.session.commit()
            flash("Participant added to event", "success")
    return redirect(url_for('main.event_participants_view', event_id=event_id))

@main_bp.route('/event/<int:event_id>/participant/<int:pid>/remove', methods=['POST'])
@login_required
@require_roles('admin', 'staff')
def remove_participant_from_event(event_id, pid):
    event = Event.query.get_or_404(event_id)
    p = Participant.query.get_or_404(pid)
    if p in event.participants:
        event.participants.remove(p)
        db.session.commit()
        flash("Participant removed from event", "info")
    return redirect(url_for('main.event_participants_view', event_id=event_id))
