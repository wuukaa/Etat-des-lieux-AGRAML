from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import uuid

db = SQLAlchemy()
DB_NAME = 'agraml.db'

def create_app():
    app = Flask(__name__)
    secrey_key = uuid.uuid4().hex
    app.config['SECRET_KEY'] = "meow" #secrey_key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .blueprints.views import views
    from .blueprints.auth import auth
    from .blueprints.edition import edition
    from .blueprints.edl import edl

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(edition, url_prefix = '/')
    app.register_blueprint(edl, url_prefix = '/')
    
    from .models import User

    with app.app_context():
        db.create_all()

    # How we load the users
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.init_app(app)
        with app.app_context():
            db.create_all()
        print('Created database!')