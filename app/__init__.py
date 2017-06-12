from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_uploads import UploadSet, configure_uploads, IMAGES
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    db.init_app(app)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True


    login_manager.init_app(app)
    admin = Admin(app,name='The New Blog',template_mode='bootstrap3')
    from app.models import User, Post, Category, Role
    from .admin_view import NewBlogModelView
    admin.add_view(NewBlogModelView(User, db.session))
    admin.add_view(NewBlogModelView(Post, db.session))
    admin.add_view(NewBlogModelView(Category, db.session))
    admin.add_view(NewBlogModelView(Role, db.session))




    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')





    return app
