from flask import Blueprint, render_template
from flask import *
from . import db
from flask_login import login_required, current_user
from .models import *
from sqlalchemy.exc import IntegrityError
#import data_management as data
import re
import unicodedata

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


# current_user - if someone is logged in can change required code
# { % if user.is_authenticated %} - show some parts of the nav bar and hide others

views = Blueprint('views', __name__)


@views.route('/home',methods=['GET', 'POST'])
#@login_required
def home():
    posts = forum_questions.query.order_by(forum_questions.time_asked.desc()).all()
    #return render_template('home.html', posts=posts)
    return render_template('home.html')


@views.route('/ask.html', methods=['GET', 'POST'])
#@login_required  # Only allow logged-in users to ask questions
def ask():
    if request.method == 'POST':
        question = request.form['question']

        # Generate slug
        base_slug = slugify(question[:50])
        slug = generate_unique_slug(base_slug)

        new_question = forum_questions(
            question=question,
            user_id=current_user.id,  
            slug=slug
        )

        db.session.add(new_question)
        try:
            db.session.commit()
            flash('Your question has been submitted!', 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('ask.html')


def generate_unique_slug(base_slug):
    slug = base_slug
    counter = 1
    while forum_questions.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

# ask question
# make custom pages for each question
# login/signup
# assignments
# admin view - simple using bootstrap
#

