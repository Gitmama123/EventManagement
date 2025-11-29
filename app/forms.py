# app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateField, TimeField,
    SelectField, IntegerField, SubmitField, PasswordField
)
from wtforms.validators import (
    DataRequired, NumberRange, Email, Length, Regexp, Optional, EqualTo
)

# Venue form
class VenueForm(FlaskForm):
    name = StringField('Venue Name', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')

# Event form
class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    venue_id = SelectField('Venue', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')

# Resource form
class ResourceForm(FlaskForm):
    name = StringField('Resource Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')

# Participant form
class ParticipantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email(message="Enter a valid email")])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(min=10, max=15, message="Phone number must be between 10–15 digits"),
        Regexp(r'^\+?\d{10,15}$', message="Phone number must contain only digits (optional +)")
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')

# User form for Admin UI
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=6, message="Password must be 6+ chars"),
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        Optional(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[('admin','admin'), ('staff','staff'), ('viewer','viewer')], validators=[DataRequired()])
    submit = SubmitField('Save')
