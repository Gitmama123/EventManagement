# app/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # admin, staff, viewer

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Venue, Resource, Event, Participant and association model ---

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)

    resources_list = db.relationship('Resource', back_populates='venue', cascade='all, delete-orphan')
    events = db.relationship('Event', backref='venue', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Venue {self.name}>'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    venue = db.relationship('Venue', back_populates='resources_list')

    def __repr__(self):
        return f'<Resource {self.name} x{self.quantity} @ venue {self.venue_id}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    # association objects
    participant_assoc = db.relationship('EventParticipant', back_populates='event', cascade='all, delete-orphan')

    # convenience relationship to get Participant objects directly
    participants = db.relationship('Participant', secondary='event_participants', back_populates='events')

    def __repr__(self):
        return f'<Event {self.title}>'

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # association objects
    event_assoc = db.relationship('EventParticipant', back_populates='participant', cascade='all, delete-orphan')

    # convenience relationship to get Event objects directly
    events = db.relationship('Event', secondary='event_participants', back_populates='participants')

    def __repr__(self):
        return f'<Participant {self.name} ({self.email})>'

class EventParticipant(db.Model):
    """
    Association object between Event and Participant.
    Stores attendance_status: 'not_marked' | 'present' | 'absent'
    """
    __tablename__ = 'event_participants'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), primary_key=True)
    attendance_status = db.Column(db.String(20), nullable=False, default='not_marked')

    # relationships back to owning models
    event = db.relationship('Event', back_populates='participant_assoc')
    participant = db.relationship('Participant', back_populates='event_assoc')

    def __repr__(self):
        return f'<EventParticipant event={self.event_id} participant={self.participant_id} status={self.attendance_status}>'
