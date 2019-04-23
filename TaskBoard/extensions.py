from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
toolbar = DebugToolbarExtension()
login_manager.login_view = 'auth.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    from TaskBoard.models import User
    user = User.query.get(int(user_id))
    return user
