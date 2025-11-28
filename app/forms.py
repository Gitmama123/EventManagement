from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateField, TimeField,
    SelectField, IntegerField, SubmitField
)
from wtforms.validators import (
    DataRequired, NumberRange, Email, Length, Regexp, Optional
)


class VenueForm(FlaskForm):
    name = StringField('Venue Name', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    venue_id = SelectField('Venue', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')

class ResourceForm(FlaskForm):
    name = StringField('Resource Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')

class ParticipantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message="Enter a valid email")])
    phone = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=15, message="Phone number must be between 10–15 digits"),
        Regexp(r'^\+?\d{10,15}$', message="Phone number must contain only digits (optional +)")
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')


