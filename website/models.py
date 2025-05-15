from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint


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

class ForumReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    time_posted = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('forum_questions.id'), nullable=False)
    user = db.relationship('User', backref='replies')
    question = db.relationship('forum_questions', backref='replies')

class Assignment(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date    = db.Column(db.DateTime)
    test_cases  = db.relationship('TestCase', backref='assignment', lazy=True)
    submissions = db.relationship('Submission', backref='assignment', lazy=True)

class TestCase(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    assignment_id  = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    input_data     = db.Column(db.Text, nullable=False)
    expected_output= db.Column(db.Text, nullable=False)

class Submission(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    code_filename  = db.Column(db.String(300), nullable=False)
    input_data     = db.Column(db.Text)                 # optional custom stdin
    output_data    = db.Column(db.Text)                 # JDoodle output
    status         = db.Column(db.String(50), default='Pending')
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id  = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    time_submitted = db.Column(db.DateTime(timezone=True), default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'assignment_id', name='uq_user_assignment'),
    )

class Announcement(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    message      = db.Column(db.Text, nullable=False)
    time_posted  = db.Column(db.DateTime(timezone=True), default=func.now())
    

