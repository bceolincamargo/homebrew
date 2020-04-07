from flask import Flask 
from flask_pymongo import PyMongo


app = Flask(__name__, template_folder='../templates',static_url_path='', static_folder='../static',)

app.config['MONGO_DBNAME'] = 'brewpiless'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1'
 
from app import routes
SECRET_KEY = 'my secret'
app.config['SECRET_KEY'] = SECRET_KEY 

