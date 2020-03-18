from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField
from flask_wtf import FlaskForm

class CreateEditBeer(FlaskForm):
    beername = StringField('beername', [validators.DataRequired(message='Name is required')])
    beerstyle = StringField('beerstyle', [validators.DataRequired(message='Style is required')])
    description = StringField('description', [validators.DataRequired(message='Description is required')])  
    submit = SubmitField('Submit')