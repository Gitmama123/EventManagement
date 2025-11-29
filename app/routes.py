# app/routes.py
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app, abort
)
from flask_login import login_required, current_user
from . import db
from .models import Venue, Event, Resource, Participant, EventParticipant, User
from .utils import require_roles
from datetime import datetime, date, timedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from .forms import UserForm
from .models import User
from sqlalchemy.exc import IntegrityError

main_bp = Blueprint('main', __name__)


# ----------------- Helpers -----------------
def is_conflict(venue_id, date_, start, end, ignore_id=None):
    """Return True if [start, end) conflicts with existing events at the same venue on date_."""
    events = Event.query.filter_by(venue_id=venue_id, date=date_).all()
    for e in events:
        if ignore_id and e.id == ignore_id:
            continue
        if (start < e.end_time and end > e.start_time):
            return True
    return False


def flash_form_errors(form):
    """Log and flash a short validation summary if form has errors."""
    messages = []
    for field, errs in form.errors.items():
        for e in errs:
            messages.append(f"{field}: {e}")
    if messages:
        flash("Please fix the form errors and try again.", "danger")
        current_app.logger.debug("Form errors: %s", messages)


# ----------------- Root -----------------
@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))


# ----------------- Dashboard -----------------
@main_bp.route('/dashboard')
@login_required
def dashboard():
    total_events = Event.query.count()
    total_venues = Venue.query.count()
    total_participants = Participant.query.count()
    total_resources = Resource.query.count()

    today = date.today()
    events_today = Event.query.filter_by(date=today).order_by(Event.start_time).all()
    events_today_count = len(events_today)

    # next 7 days data
    days = []
    day_counts = []
    for i in range(0, 7):
        d = today + timedelta(days=i)
        days.append(d.strftime('%a %d %b'))
        cnt = Event.query.filter_by(date=d).count()
        day_counts.append(cnt)

    # upcoming events (14 days)
    upcoming_limit = today + timedelta(days=14)
    upcoming_events = (
        Event.query.filter(Event.date >= today, Event.date <= upcoming_limit)
        .order_by(Event.date, Event.start_time)
        .all()
    )

    # busiest venue next 30 days
    window_end = today + timedelta(days=30)
    venue_counts = (
        db.session.query(Venue.id, Venue.name, func.count(Event.id).label('ev_count'))
        .join(Event, Event.venue_id == Venue.id)
        .filter(Event.date >= today, Event.date <= window_end)
        .group_by(Venue.id)
        .order_by(func.count(Event.id).desc())
        .limit(1)
        .all()
    )
    busiest_venue = venue_counts[0] if venue_counts else None

    # Attendance summary for today's events
    attendance_summary = []
    for e in events_today:
        total = db.session.query(EventParticipant).filter_by(event_id=e.id).count()
        present = db.session.query(EventParticipant).filter_by(event_id=e.id, attendance_status='present').count()
        absent = db.session.query(EventParticipant).filter_by(event_id=e.id, attendance_status='absent').count()
        not_marked = db.session.query(EventParticipant).filter_by(event_id=e.id, attendance_status='not_marked').count()
        rate = (present / total * 100) if total > 0 else 0
        attendance_summary.append({
            "event": e,
            "total": total,
            "present": present,
            "absent": absent,
            "not_marked": not_marked,
            "rate": round(rate, 1)
        })

    return render_template(
        'dashboard.html',
        total_events=total_events,
        total_venues=total_venues,
        total_participants=total_participants,
        total_resources=total_resources,
        events_today=events_today,
        events_today_count=events_today_count,
        days=days,
        day_counts=day_counts,
        upcoming_events=upcoming_events,
        busiest_venue=busiest_venue,
        attendance_summary=attendance_summary
    )


# ----------------- Venue routes -----------------
@main_bp.route('/venues')
@login_required
def list_venues():
    venues = Venue.query.order_by(Venue.name).all()
    return render_template('venues/list.html', venues=venues)


@main_bp.route('/venue/add', methods=['GET', 'POST'])
@login_required
@require_roles('admin')
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


@main_bp.route('/venue/<int:venue_id>/edit', methods=['GET', 'POST'])
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


# ----------------- Resource routes -----------------
@main_bp.route('/venue/<int:venue_id>/resources')
@login_required
def manage_resources(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    return render_template('venues/resources.html', venue=venue)


@main_bp.route('/venue/<int:venue_id>/resource/add', methods=['GET', 'POST'])
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


@main_bp.route('/resource/<int:res_id>/edit', methods=['GET', 'POST'])
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


# ----------------- Event routes -----------------
@main_bp.route('/events')
@login_required
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


@main_bp.route('/event/add', methods=['GET', 'POST'])
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


@main_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
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
    flash('Event deleted', 'info')
    return redirect(url_for('main.list_events'))


# ----------------- Participant routes -----------------
@main_bp.route('/participants')
@login_required
def list_participants():
    participants = Participant.query.order_by(Participant.name).all()
    return render_template('participants/list.html', participants=participants)


@main_bp.route('/participant/add', methods=['GET', 'POST'])
@login_required
@require_roles('admin', 'staff')
def add_participant():
    from .forms import ParticipantForm
    form = ParticipantForm()
    if form.validate_on_submit():
        # Create participant without passing unknown kwargs directly
        p = Participant(
            name=form.name.data.strip(),
            email=form.email.data.strip() if form.email.data else None,
            phone=form.phone.data.strip() if form.phone.data else None
        )
        # set notes only if attribute exists on model
        if hasattr(p, 'notes'):
            p.notes = form.notes.data
        db.session.add(p)
        db.session.commit()
        flash("Participant added", "success")
        return redirect(url_for('main.list_participants'))
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('participants/add_edit.html', form=form, action="Add")


@main_bp.route('/participant/<int:pid>/edit', methods=['GET', 'POST'])
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
        # update notes safely
        if hasattr(p, 'notes'):
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
    # Delete association rows explicitly
    EventParticipant.query.filter_by(participant_id=p.id).delete()
    db.session.delete(p)
    db.session.commit()
    flash("Participant deleted", "info")
    return redirect(url_for('main.list_participants'))


# ----------------- Event <-> Participant (association-aware) -----------------
@main_bp.route('/event/<int:event_id>/participants')
@login_required
def event_participants_view(event_id):
    event = Event.query.get_or_404(event_id)
    # participants available to add (not already in event)
    available = Participant.query.filter(~Participant.events.any(id=event.id)).order_by(Participant.name).all()
    # current participants via association objects
    assocs = EventParticipant.query.filter_by(event_id=event.id).join(Participant).order_by(Participant.name).all()
    return render_template('events/participants.html', event=event, available=available, assocs=assocs)


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
    # check existing association
    exists = EventParticipant.query.filter_by(event_id=event.id, participant_id=p.id).first()
    if exists:
        flash("Participant already registered for this event", "warning")
        return redirect(url_for('main.event_participants_view', event_id=event_id))

    # capacity check
    if event.venue and event.venue.capacity and EventParticipant.query.filter_by(event_id=event.id).count() >= event.venue.capacity:
        flash("Cannot add participant — venue capacity reached.", "danger")
        return redirect(url_for('main.event_participants_view', event_id=event_id))

    assoc = EventParticipant(event_id=event.id, participant_id=p.id, attendance_status='not_marked')
    db.session.add(assoc)
    db.session.commit()
    flash("Participant added to event", "success")
    return redirect(url_for('main.event_participants_view', event_id=event_id))


@main_bp.route('/event/<int:event_id>/participant/<int:pid>/remove', methods=['POST'])
@login_required
@require_roles('admin', 'staff')
def remove_participant_from_event(event_id, pid):
    assoc = EventParticipant.query.filter_by(event_id=event_id, participant_id=pid).first()
    if assoc:
        db.session.delete(assoc)
        db.session.commit()
        flash("Participant removed from event", "info")
    else:
        flash("Participant not registered for event", "warning")
    return redirect(url_for('main.event_participants_view', event_id=event_id))

# === Admin user management routes ===
@main_bp.route('/admin/users')
@login_required
@require_roles('admin')
def admin_list_users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=users)

@main_bp.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
@require_roles('admin')
def admin_add_user():
    form = UserForm()
    if form.validate_on_submit():
        try:
            u = User(username=form.username.data.strip(), role=form.role.data)
            if form.password.data:
                u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            flash('User created', 'success')
            return redirect(url_for('main.admin_list_users'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists', 'danger')
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('admin/edit_user.html', form=form, action='Add')

@main_bp.route('/admin/user/<int:uid>/edit', methods=['GET', 'POST'])
@login_required
@require_roles('admin')
def admin_edit_user(uid):
    user = User.query.get_or_404(uid)
    form = UserForm(obj=user)
    # Do not prefill password fields
    form.password.data = ''
    form.password_confirm.data = ''
    if form.validate_on_submit():
        user.username = form.username.data.strip()
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        try:
            db.session.commit()
            flash('User updated', 'success')
            return redirect(url_for('main.admin_list_users'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists', 'danger')
    if request.method == 'POST' and not form.validate():
        flash_form_errors(form)
    return render_template('admin/edit_user.html', form=form, action='Edit', user=user)

@main_bp.route('/admin/user/<int:uid>/delete', methods=['POST'])
@login_required
@require_roles('admin')
def admin_delete_user(uid):
    user = User.query.get_or_404(uid)
    if user.username == current_user.username:
        flash("You cannot delete your own account while logged in.", "warning")
        return redirect(url_for('main.admin_list_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'info')
    return redirect(url_for('main.admin_list_users'))



# ----------------- Attendance routes -----------------
@main_bp.route('/event/<int:event_id>/attendance')
@login_required
@require_roles('admin', 'staff')
def event_attendance_view(event_id):
    event = Event.query.get_or_404(event_id)
    assocs = EventParticipant.query.filter_by(event_id=event.id).join(Participant).order_by(Participant.name).all()
    return render_template('events/attendance.html', event=event, assocs=assocs)


@main_bp.route('/event/<int:event_id>/attendance/update', methods=['POST'])
@login_required
@require_roles('admin', 'staff')
def update_event_attendance(event_id):
    event = Event.query.get_or_404(event_id)

    # Quick debug: log what form fields were posted (useful during dev)
    current_app.logger.debug("Attendance POST data: %s", dict(request.form))

    # 1) Single-update path (AJAX or single-field form)
    pid = request.form.get('participant_id')
    status = request.form.get('status')
    if pid and status:
        assoc = EventParticipant.query.filter_by(event_id=event.id, participant_id=int(pid)).first()
        if not assoc:
            flash("Participant not registered.", "danger")
            return redirect(url_for('main.event_attendance_view', event_id=event_id))
        assoc.attendance_status = status
        db.session.commit()
        flash("Attendance updated.", "success")
        return redirect(url_for('main.event_attendance_view', event_id=event_id))

    # 2) Batch update: fields like status_<participant_id>
    updated = 0
    received = {}  # for clearer feedback
    for key, val in request.form.items():
        if not key.startswith('status_'):
            continue
        try:
            p_id = int(key.split('_', 1)[1])
        except Exception:
            current_app.logger.debug("Skipping malformed attendance key: %s", key)
            continue
        received[p_id] = val
        assoc = EventParticipant.query.filter_by(event_id=event.id, participant_id=p_id).first()
        if assoc:
            if assoc.attendance_status != val:
                assoc.attendance_status = val
                updated += 1
        else:
            current_app.logger.debug("No association row for event %s participant %s", event.id, p_id)

    if updated:
        db.session.commit()
        flash(f"Updated attendance for {updated} participant(s).", "success")
    else:
        if received:
            rstr = ", ".join(f"{k}:{v}" for k, v in received.items())
            flash(f"No attendance changes detected. Received: {rstr}", "info")
        else:
            flash("No attendance fields were found in the submitted form.", "warning")

    return redirect(url_for('main.event_attendance_view', event_id=event_id))
