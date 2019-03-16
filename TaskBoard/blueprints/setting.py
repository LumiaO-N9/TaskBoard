from flask import Blueprint, render_template, request
from TaskBoard.models import Project, User
from TaskBoard.extensions import db
from flask_login import login_required

setting_bp = Blueprint('setting', __name__)


@setting_bp.before_request
@login_required
def login_project():
    pass


@setting_bp.route('/')
def index():
    projects = Project.query.order_by(Project.title).all()
    users = User.query.order_by(User.is_admin.desc()).all()
    return render_template('setting/settings.html', projects=projects, users=users)


@setting_bp.route('/change-default-board', methods=['POST'])
def change_default_board():
    project_id = request.form['project_id']
    user_id = request.form['user_id']
    print(user_id)
    try:
        user = User.query.get(user_id)
        user.default_project_id = project_id
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return "ok"


@setting_bp.route('/chang-project-status', methods=['POST'])
def change_project_status():
    project_id = request.form['project_id']
    try:
        project = Project.query.get(project_id)
        status = project.status
        project.status = not status
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/sort-by-name')
def sort_by_name():
    projects = Project.query.order_by(Project.title).all()
    return render_template('_ProjectsTable.html', projects=projects)


@setting_bp.route('/sort-by-date')
def sort_by_date():
    projects = Project.query.order_by(Project.createtime).all()
    return render_template('_ProjectsTable.html', projects=projects)


@setting_bp.route('/del-user-by-id', methods=['POST'])
def del_user_by_id():
    user_id = request.form['user_id']
    try:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/del-project-by-id', methods=['POST'])
def del_project_by_id():
    project_id = request.form['project_id']
    try:
        project = Project.query.get(project_id)
        db.session.delete(project)
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/save-user-edit-modal', methods=["POST"])
def save_user_edit_modal():
    user_id = request.form['user_id']
    username = request.form['username']
    password = request.form['password1']
    email = request.form['email']
    default_board_id = request.form['default_board']
    try:
        user = User.query.get(user_id)
        if username:
            user.username = username
        if password:
            user.set_password(password)
        if email:
            user.email = email
        if default_board_id != 'None':
            user.default_project_id = default_board_id
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'
