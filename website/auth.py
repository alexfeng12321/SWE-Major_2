from flask import Blueprint, render_template, request
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/index', methods=['GET', 'POST'])
@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        data = request.form
    return render_template('index.html')
    #return render_template("Login.html")

    #return render_template("login.html", text="testing")


#new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
'''
@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    pass
'''

@auth.route('/Login', methods=['GET', 'POST'])
def signup():
    pass


'''
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)
'''