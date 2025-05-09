from flask import Blueprint, render_template
from flask import *
from . import db
from flask_login import login_required, current_user
from .models import *


# current_user - if someone is logged in can change required code
# { % if user.is_authenticated %} - show some parts of the nav bar and hide others

views = Blueprint('views', __name__)

def test():
    post1 = forum_questions(
    content='How do I configure PowerShell task scheduler properly?',
    name='Alice',
    question_type='PowerShell',
    #slug='configure-powershell-task-scheduler'
    )

    db.session.add(post1)
    db.session.commit()
    

@views.route('/home',methods=['GET', 'POST'])
#@login_required
def home():
    if request.method == 'POST':    
        test()
    posts = forum_questions.query.order_by(forum_questions.time_asked.desc()).all()
    return render_template('home.html', posts=posts)



@views.route('/Ask-Question.html', methods=['GET', 'POST'])
def ask_question():
    if request.method == "POST":
        print("hellow world")
        return render_template("Ask-Question.html")

    return render_template("Ask-Question.html")

# make custom pages for each question
# ask question
# login/signup
