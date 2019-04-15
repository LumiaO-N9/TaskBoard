from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, logout_user, login_required
from TaskBoard.forms import LoginForm
from TaskBoard.models import User
from TaskBoard.utils import redirect_back
import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('taskboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(username=username).first()
        if user:
            if user.validate_password(password):
                duration = datetime.timedelta(days=7)
                login_user(user, remember, duration=duration)
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('auth.login'))
