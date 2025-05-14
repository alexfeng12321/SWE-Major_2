from flask import Blueprint, render_template
from flask import *
#from . import db
from flask_login import login_required, current_user
from .models import *
from sqlalchemy.exc import IntegrityError
#import data_management as data
import re
import unicodedata
# Use actual user IDs from your User table

user_id = 1  # Replace with valid user ID

def slugify(text):
    # Ensure text is a str (in case bytes slip in)
    if not isinstance(text, str):
        text = text.decode('utf-8')

    # Normalize accents/diacritics
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Replace non-word characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    
    # Replace spaces and multiple hyphens with a single hyphen
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    
    return text


q1 = forum_questions(
    question="How do I install Flask on Windows?",
    slug=slugify("How do I install Flask on Windows?"),
    user_id=user_id
)

q2 = forum_questions(
    question="Why am I getting a KeyError in Python dictionaries?",
    slug=slugify("Why am I getting a KeyError in Python dictionaries?"),
    user_id=user_id
)

q3 = forum_questions(
    question="What is the best way to structure a Flask project?",
    slug=slugify("What is the best way to structure a Flask project?"),
    user_id=user_id
)

db.session.add_all([q1, q2, q3])
db.session.commit()