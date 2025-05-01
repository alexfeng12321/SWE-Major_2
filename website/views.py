from flask import Blueprint, render_template
from flask_login import login_required, current_user


# current_user - if someone is logged in can change required code
# { % if user.is_authenticated %} - show some parts of the nav bar and hide others

views = Blueprint('views', __name__)


@views.route('/home')
@login_required
def home():
    return "<p> hello world </p>"

