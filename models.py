from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    capacity = db.Column(db.Integer)

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  # 'organizer' or 'attendee'
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # Plaintext for demo only
