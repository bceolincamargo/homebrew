from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField
from flask_wtf import FlaskForm

class CreateEditBeer(FlaskForm):
    beername = StringField('Beer Name', [validators.DataRequired(message='Name is required')])
    beerstyle = StringField('Beer Style', [validators.DataRequired(message='Style is required')])
    description = StringField('Description', [validators.DataRequired(message='Description is required')])  
    created = StringField('Created')  
    finished = StringField('Finished')      
    Save = SubmitField('Save')


class SearchBeer(FlaskForm):
    beername = StringField('beername')
    beerstyle = StringField('beerstyle')
    Search = SubmitField('Search')    