from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    searchField = db.Column(db.String(1000), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    img = db.Column(db.String(256), nullable=True)
    searchField = db.Column(db.String(1000), nullable=False)

class Carousel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(256), nullable=True)
    title = db.Column(db.String(256), nullable=True)
    desc = db.Column(db.String(500), nullable=False)
    text_positon = db.Column(db.String(50), nullable=False)
    button_text = db.Column(db.String(128), nullable=False)
    button_link = db.Column(db.String(128), nullable=False)
