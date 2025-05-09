from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

class forum_questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(100), nullable=False)  
    question_type = db.Column(db.String(100), nullable=False)
    time_asked = db.Column(db.DateTime(timezone=True), default=func.now())
    #slug = db.Column(db.String(150), unique=False, nullable=False) 


'''
e.g link notes to user
user_id = db.column(db.Integer, db.ForeignKey('user.id))

in user:
notes = db.relationship('note)

'''