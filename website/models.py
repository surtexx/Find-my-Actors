from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    password = db.Column(db.String(150))



class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(500))
    image = db.Column(db.String(150))


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150))
    actorid = db.Column(db.Integer, db.ForeignKey('actor.id'))



