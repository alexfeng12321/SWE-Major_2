from flask import *
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()
DB_NAME = 'database.db'

from .models import *


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' #sql lite database is stored here
    db.init_app(app) # use this app with this database

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    from .models import forum_questions

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.config.from_object("website.config")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    admin = Admin(
        app,
        name="Programing Club Admin",
        template_mode="bootstrap3",
        url="/admin"
    
    )


    class SecureModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.is_admin
        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('auth.login'))
        

    class TestCaseAdmin(ModelView):
        form_columns = ['assignment_id', 'input_data', 'expected_output']


    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(forum_questions, db.session, name="Questions", category="Forum"))
    admin.add_view(SecureModelView(ForumReply, db.session, name="Replies", category="Forum"))
    admin.add_view(SecureModelView(Announcement, db.session, name="Announcements", category="Site"))
    admin.add_view(SecureModelView(Assignment, db.session, name="Assignments", category="Assignments"))
    admin.add_view(TestCaseAdmin(TestCase, db.session, name="Test Cases", category="Assignments"))
    admin.add_view(SecureModelView(Submission, db.session, name="Submissions", category="Assignments"))


    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():  # Ensure the app context is active
            db.create_all()
        print('Created Database!')
