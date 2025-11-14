from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class VenueForm(FlaskForm):
    name = StringField('Venue Name', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=0)])
    resources = TextAreaField('Resources')
    submit = SubmitField('Save')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    venue_id = SelectField('Venue', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')
