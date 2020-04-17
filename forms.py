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


class Yeasts(FlaskForm):
    Yeast = StringField('Yeast')
    Yeastlab = StringField('Yeastlab')
    Yeasttype = StringField('Yeasttype')   
    
class CreateEditYeast(FlaskForm):
    yeast = StringField('Yeast')
    lab = StringField('Lab')
    typey = StringField('Typey')  
    formato = StringField('Formato')  
    temp = StringField('Temp')      
    att = StringField('Att')         
    flo = StringField('Flo')      
    notes = StringField('Notes')         
    Save = SubmitField('Save')    

class Hops(FlaskForm):
    Hop = StringField('Hop')
    Type = StringField('Type')
    Origin = StringField('Origin')

class CreateEditHop(FlaskForm):
    hop = StringField('Hop')
    origin = StringField('Origin')
    hoptype = StringField('hoptype')  
    alpha = StringField('Alpha')  
    beta = StringField('Beta')      
    notes = StringField('Notes')         
    Save = SubmitField('Save')
    
    
class Grains(FlaskForm):
    Grain = StringField('Grain')
    Origin = StringField('Origin')    
    Mash = StringField('Mash')

class CreateEditGrain(FlaskForm):
    grain = StringField('Grain')
    origin = StringField('Origin')
    mash = StringField('Mash')  
    color = StringField('Color')  
    power = StringField('Power')      
    potential = StringField('Potential')         
    maxp = StringField('Maxp')      
    notes = StringField('Notes')         
    Save = SubmitField('Save')    
    