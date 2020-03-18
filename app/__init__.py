from flask import Flask 
#from flask_minify import minify


app = Flask(__name__, template_folder='../templates',static_url_path='', static_folder='../static',)
 
from app import routes
SECRET_KEY = 'my secret'
app.config['SECRET_KEY'] = SECRET_KEY 