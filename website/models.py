from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')


'''
e.g link notes to user
user_id = db.column(db.Integer, db.ForeignKey('user.id))

in user:
notes = db.relationship('note)

'''