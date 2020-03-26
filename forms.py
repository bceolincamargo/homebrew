from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField
from flask_wtf import FlaskForm

class CreateEditBeer(FlaskForm):
    beername = StringField('beername')
    beerstyle = StringField('beerstyle')
    description = StringField('description')  
    created = StringField('created')  
    finished = StringField('finished')      
    Save = SubmitField('Save')


class SearchBeer(FlaskForm):
    beername = StringField('beername')
    beerstyle = StringField('beerstyle')
    Search = SubmitField('Search')    