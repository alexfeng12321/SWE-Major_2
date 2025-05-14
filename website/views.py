from flask import Blueprint, render_template, abort
from flask import *
from . import db
from flask_login import login_required, current_user
from .models import *
from sqlalchemy.exc import IntegrityError
from .tasks import grade_submission
import os
from werkzeug.utils import secure_filename
from website.config import ALLOWED_EXTENSIONS

import re
import unicodedata


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

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


@views.route('/home.html',methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        print(url)
        return redirect(url, code=302)
    posts = forum_questions.query.order_by(forum_questions.time_asked.desc()).all()
    assignments = Assignment.query.order_by(Assignment.due_date).all()

    #return render_template('home.html', posts=posts)
    return render_template('home.html', user=current_user, posts=posts, assignments=assignments)


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
            return redirect(url_for('views.home'))
        except IntegrityError:
            db.session.rollback()
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        print(url)
        return redirect(url, code=302)
    return render_template('ask.html', user=current_user)


def generate_unique_slug(base_slug):
    slug = base_slug
    counter = 1
    while forum_questions.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug



@views.route('/question/<slug>')
def reply(slug):
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        print(url)
        return redirect(url, code=302)
    post = forum_questions.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    replies = ForumReply.query.filter_by(question_id=post.id).all()
    return render_template('reply.html', post=post, replies=replies)


@views.route('/question/<slug>/reply', methods=['POST'])
@login_required
def add_reply(slug):
    post = forum_questions.query.filter_by(slug=slug).first_or_404()
    content = request.form.get('content')
    if content:
        reply = ForumReply(content=content, user_id=current_user.id, question_id=post.id)
        db.session.add(reply)
        db.session.commit()
    return redirect(url_for('views.reply', slug=slug))

@views.route('/assignment.html', methods=['GET', 'POST'])
def assignments():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        print(url)
        return redirect(url, code=302)

    return render_template("assignments.html")



@views.route('/assignments/<int:a_id>/submit', methods=['GET','POST'])
@login_required
def submit_assignment(a_id):
    assignment = Assignment.query.get_or_404(a_id)
    if request.method == 'POST':
        file = request.files['file']
        input_data = request.form.get('input_data','')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            sub = Submission(
                code_filename=filename,
                input_data=input_data,
                user_id=current_user.id,
                assignment_id=a_id
            )
            db.session.add(sub)
            db.session.commit()
            grade_submission.delay(sub.id)

            flash('Submitted! Grading in progress…', 'info')
            return redirect(url_for('views.assignment_detail', a_id=a_id))

    return render_template('submit.html', assignment=assignment)



# announcements
# assignments
# admin view - simple using bootstrap
# header view change 
# logout


'''
<!--
        <a
          href="{{ url_for('single_post', slug=post.slug) }}"
          class="u-active-none u-blog-control u-border-2 u-border-no-left u-border-no-right u-border-no-top u-border-palette-1-base u-btn u-btn-rectangle u-button-style u-hover-none u-none u-btn-4"
        >
          Read More
        </a>
        -->
        
        
'''

