# app/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# association table for many-to-many between Event and Participant
event_participants = db.Table(
    'event_participants',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('participant_id', db.Integer, db.ForeignKey('participant.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)

    # relationship to Resource (one-to-many)
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

    # many-to-many participants
    participants = db.relationship('Participant', secondary=event_participants, back_populates='events')

    def __repr__(self):
        return f'<Event {self.title}>'

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # backref to events
    events = db.relationship('Event', secondary=event_participants, back_populates='participants')

    def __repr__(self):
        return f'<Participant {self.name} ({self.email})>'
