from flask import Blueprint, render_template
from flask import *
from flask_login import login_required, current_user


# current_user - if someone is logged in can change required code
# { % if user.is_authenticated %} - show some parts of the nav bar and hide others

views = Blueprint('views', __name__)


@views.route('/home',methods=['GET', 'POST'])
#@login_required
def home():
    return render_template("home.html")



@views.route('Ask-Question.html', methods=['GET', 'POST'])
def ask_question():
    if request.method == "POST":
        print("hellow world")
        return render_template("Ask-Question.html")

    return render_template("Ask-Question.html")
