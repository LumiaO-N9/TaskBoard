from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_user, logout_user
from TaskBoard.forms import LoginForm
from TaskBoard.models import User
from TaskBoard.utils import is_safe_url
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
                next_path = '/'
                for target in request.args.get('next'), request.referrer:
                    if not target:
                        continue
                    if is_safe_url(target):
                        next_path_array = target.split('next=')
                        if len(next_path_array) > 1:
                            next_path = next_path_array[1].replace('%2F', '/')
                return next_path
            # flash('Invalid username or password.', 'warning')
            return 'invalid'
        else:
            # flash('No account.', 'danger')
            return 'danger'
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('auth.login'))
