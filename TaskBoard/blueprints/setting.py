from flask import Blueprint, render_template, request
from TaskBoard.models import Project, User
from flask_login import login_required

setting_bp = Blueprint('setting', __name__)


@setting_bp.before_request
@login_required
def login_project():
    pass


@setting_bp.route('/')
def index():
    projects = Project.query.all()
    users = User.query.order_by(User.is_admin.desc()).all()
    return render_template('setting/settings.html', projects=projects, users=users)


@setting_bp.route('/change-default-board', methods=['POST'])
def change_default_board():
    project_id = request.form['project_id']
    user_id = request.form['user_id']

    return "1"
