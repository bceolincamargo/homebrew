from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField, SelectField
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

class CreateRecipe(FlaskForm): 
    name = StringField('name')
    grain = StringField('grains')
    hop = StringField('hop')  
    yeast = StringField('yeast')  
    fermentable = StringField('fermentable')      
    Save = SubmitField('Save')


class Yeasts(FlaskForm):
    Yeast = StringField('Yeast')
    Yeastlab = StringField('Yeastlab')
    Yeasttype = StringField('Yeasttype')   
    
class CreateEditYeast(FlaskForm):
    yeast = StringField('Name')
    lab = StringField('Lab')
    typey = StringField('Type')  
    formato = StringField('Form')  
    temp = StringField('Temp')      
    att = StringField('Attenuation')         
    flo = StringField('Flocculation')      
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
    