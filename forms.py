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
    
class Recipe(FlaskForm):
    beername = StringField('beername')
    beerstyle = StringField('beerstyle')
    description = StringField('description')  
    created = StringField('created')  
    finished = StringField('finished')      
    Save = SubmitField('Save')


class Yeast(FlaskForm):
    yeastname = StringField('yeastname')
    description = StringField('description')
    yeasttype = StringField('yeasttype')  
    attenuationmin = StringField('attenuationmin')  
    attenuationmax = StringField('attenuationmax')      
    fermenttempmin = StringField('fermenttempmin')      
    fermenttempmax = StringField('fermenttempmax')          
    alcoholtolerancemin = StringField('alcoholtolerancemin')      
    alcoholtolerancemax = StringField('alcoholtolerancemax')      
    supplier = StringField('supplier')          
    yeastformat = StringField('yeastformat')
    Save = SubmitField('Save')
    