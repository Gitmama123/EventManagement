from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Venue, Event
from . import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

def is_conflict(venue_id, date, start, end, ignore_id=None):
    events = Event.query.filter_by(venue_id=venue_id, date=date).all()
    for e in events:
        if ignore_id and e.id == ignore_id:
            continue
        if start < e.end_time and end > e.start_time:
            return True
    return False

@main_bp.route('/')
def index():
    return redirect(url_for('main.list_events'))

# ----------------- VENUE ROUTES -----------------
@main_bp.route('/venues')
def list_venues():
    venues = Venue.query.order_by(Venue.name).all()
    return render_template('venues/list.html', venues=venues)

@main_bp.route('/venue/add', methods=['GET','POST'])
@login_required
def add_venue():
    from .forms import VenueForm
    form = VenueForm()
    if form.validate_on_submit():
        v = Venue(name=form.name.data.strip(), capacity=form.capacity.data, resources=form.resources.data)
        db.session.add(v)
        db.session.commit()
        flash("Venue added", "success")
        return redirect(url_for('main.list_venues'))
    return render_template('venues/add_edit.html', form=form, action="Add")

@main_bp.route('/venue/<int:venue_id>/edit', methods=['GET','POST'])
@login_required
def edit_venue(venue_id):
    v = Venue.query.get_or_404(venue_id)
    from .forms import VenueForm
    form = VenueForm(obj=v)
    if form.validate_on_submit():
        v.name = form.name.data.strip()
        v.capacity = form.capacity.data
        v.resources = form.resources.data
        db.session.commit()
        flash("Venue updated", "success")
        return redirect(url_for('main.list_venues'))
    return render_template('venues/add_edit.html', form=form, action="Edit")

@main_bp.route('/venue/<int:venue_id>/delete', methods=['POST'])
@login_required
def delete_venue(venue_id):
    v = Venue.query.get_or_404(venue_id)
    # Prevent deletion if there are associated events (safer)
    if v.events:
        flash("Cannot delete venue with existing events. Delete its events first.", "danger")
        return redirect(url_for('main.list_venues'))
    db.session.delete(v)
    db.session.commit()
    flash("Venue deleted.", "info")
    return redirect(url_for('main.list_venues'))

# ----------------- EVENT ROUTES -----------------
@main_bp.route('/events')
def list_events():
    q_date = request.args.get('date')
    if q_date:
        try:
            dt = datetime.strptime(q_date, '%Y-%m-%d').date()
            events = Event.query.filter_by(date=dt).order_by(Event.start_time).all()
        except:
            events = Event.query.order_by(Event.date, Event.start_time).all()
    else:
        events = Event.query.order_by(Event.date, Event.start_time).all()
    return render_template('events/list.html', events=events)

@main_bp.route('/event/add', methods=['GET','POST'])
@login_required
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
    return render_template('events/add_edit.html', form=form, action="Add")

@main_bp.route('/event/<int:event_id>/edit', methods=['GET','POST'])
@login_required
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
        flash('Event updated.', 'success')
        return redirect(url_for('main.list_events'))
    return render_template('events/add_edit.html', form=form, action="Edit")

@main_bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    e = Event.query.get_or_404(event_id)
    db.session.delete(e)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('main.list_events'))
