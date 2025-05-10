from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user = db.Column(db.String(150), unique=True)

class forum_questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    #question_type = db.Column(db.String(100), nullable=False)
    time_asked = db.Column(db.DateTime(timezone=True), default=func.now())
    slug = db.Column(db.String(150), unique=False, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))


'''
e.g link notes to user
user_id = db.column(db.Integer, db.ForeignKey('user.id))

in user:
notes = db.relationship('note)

'''