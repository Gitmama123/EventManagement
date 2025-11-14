from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
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

@main_bp.route('/venues')
def list_venues():
    return render_template('venues/list.html', venues=Venue.query.all())

@main_bp.route('/venue/add', methods=['GET','POST'])
@login_required
def add_venue():
    from .forms import VenueForm
    form = VenueForm()
    if form.validate_on_submit():
        v=Venue(name=form.name.data,capacity=form.capacity.data,resources=form.resources.data)
        db.session.add(v)
        db.session.commit()
        flash("Venue added","success")
        return redirect(url_for('main.list_venues'))
    return render_template('venues/add_edit.html', form=form, action="Add")

@main_bp.route('/events')
def list_events():
    return render_template('events/list.html',
                           events=Event.query.order_by(Event.date,Event.start_time).all())

@main_bp.route('/event/add', methods=['GET','POST'])
@login_required
def add_event():
    from .forms import EventForm
    form=EventForm()
    form.venue_id.choices=[(v.id,v.name) for v in Venue.query.all()]
    if form.validate_on_submit():
        if is_conflict(form.venue_id.data,form.date.data,form.start_time.data,form.end_time.data):
            flash("Venue conflict","danger")
            return render_template('events/add_edit.html', form=form, action="Add")
        e=Event(title=form.title.data,description=form.description.data,date=form.date.data,
                start_time=form.start_time.data,end_time=form.end_time.data,venue_id=form.venue_id.data)
        db.session.add(e)
        db.session.commit()
        flash("Event added","success")
        return redirect(url_for('main.list_events'))
    return render_template('events/add_edit.html', form=form, action="Add")
