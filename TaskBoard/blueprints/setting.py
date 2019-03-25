from flask import Blueprint, render_template, request
from TaskBoard.models import Project, User, Milestone, Category
from TaskBoard.extensions import db
from flask_login import login_required, current_user

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


@setting_bp.route('/change-default-project', methods=['POST'])
def change_default_project():
    project_id = request.form['project_id']
    user_id = request.form['user_id']
    try:
        user = User.query.get(user_id)
        project = Project.query.get(project_id)
        if user.default_project != project:
            user.default_project = project
            db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return "ok"


@setting_bp.route('/change-user-password', methods=['POST'])
def change_user_password():
    current_password = request.form.get('current_password', None)
    password = request.form.get('password', None)
    try:
        user = current_user
        if not user.validate_password(current_password):
            return 'invalid'
        user.set_password(password)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return 'fail'
    return 'ok'


@setting_bp.route('/change-user-email', methods=['POST'])
def change_user_username_or_email():
    name = request.form.get('name', None)
    if not name:
        return 'fail'
    info = request.form.get('info', None)
    try:
        if name == 'email':
            if info != current_user.email and User.query.filter_by(email=info).first():
                return 'same'
            current_user.email = info
        elif name == 'username':
            if info != current_user.username and User.query.filter_by(username=info).first():
                return 'same'
            current_user.username = info
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return 'fail'
    return 'ok'


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
    return render_template('setting/_ProjectsTable.html', projects=projects)


@setting_bp.route('/sort-by-date')
def sort_by_date():
    projects = Project.query.order_by(Project.create_time).all()
    return render_template('setting/_ProjectsTable.html', projects=projects)


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
    user_id = request.form.get('user_id', None)
    username = request.form.get('username', None)
    password = request.form.get('password1', None)
    email = request.form.get('email', None)
    default_project_id = request.form.get('default_project', None)
    access_project_id = request.form.get('access_project', None)
    is_admin = request.form.get('is_admin', False)
    status = 'edit'
    try:
        if user_id:
            user = User.query.get(user_id)
        else:
            user = User()
            status = 'add'
            db.session.add(user)
        if username != user.username and User.query.filter_by(username=username).first():
            return 'same username'
        if email != user.email and User.query.filter_by(email=email).first():
            return 'same email'
        user.is_admin = False
        if username:
            user.username = username
        if password:
            user.set_password(password)
        if email:
            user.email = email
        if default_project_id:
            project = Project.query.get(default_project_id)
            user.default_project = project
        if access_project_id:
            if access_project_id == "None":
                user.access_project = None
            else:
                project = Project.query.get(access_project_id)
                user.access_project = project
                if project not in user.projects:
                    user.projects.append(project)
        if is_admin:
            user.is_admin = True
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return status


# @setting_bp.route('/save-user-add-modal', methods=["POST"])
# def save_user_add_modal():
#     username = request.form.get('username', None)
#     password = request.form.get('password1', None)
#     email = request.form.get('email', None)
#     default_project_id = request.form.get('default_project', None)
#     access_project_id = request.form.get('access_project', None)
#     is_admin = request.form.get('is_admin', False)
#     if is_admin:
#         is_admin = True
#     try:
#         user = User(
#             username=username,
#             email=email,
#             default_project_id=default_project_id,
#             access_project_id=access_project_id,
#             is_admin=is_admin
#         )
#         user.set_password(password)
#         db.session.add(user)
#         db.session.commit()
#     except Exception as e:
#         print(e)
#         return 'fail'
#     return 'ok'


@setting_bp.route('/ajax-load-project-table')
def ajax_load_project_table():
    projects = Project.query.order_by(Project.title).all()
    users = User.query.order_by(User.is_admin.desc()).all()
    return render_template('setting/_ProjectsTable.html', projects=projects, users=users)


@setting_bp.route('/ajax-load-user-table')
def ajax_load_user_table():
    projects = Project.query.order_by(Project.title).all()
    users = User.query.order_by(User.is_admin.desc()).all()
    return render_template('setting/_UsersTable.html', projects=projects, users=users)


@setting_bp.route('/save-project-edit-modal', methods=["POST"])
def save_project_edit_modal():
    json_data = request.get_json()
    print(json_data)
    project_id = json_data.get('project_id', None)
    project_title = json_data.get('project_title', None)
    order_id_array = json_data.get('order_id_array', None)
    exist_milestones_id_title = json_data.get('exist_milestones_id_title', None)
    exist_categories_id_title_color = json_data.get('exist_categories_id_title_color', None)
    wait_to_delete_milestone_id_array = json_data.get('wait_to_delete_milestone_id_array', None)
    wait_to_delete_category_id_array = json_data.get('wait_to_delete_category_id_array', None)
    wait_remove_users_id_array = json_data.get('wait_remove_users_id_array', None)
    wait_add_users_id_array = json_data.get('wait_add_users_id_array', None)
    order = 0
    status = 'edit'
    try:
        if project_id:
            project = Project.query.get(project_id)
        else:
            project = Project()
            status = 'add'
            db.session.add(project)
        if project.title != project_title:
            project.title = project_title
        for i in wait_remove_users_id_array:
            user = User.query.get(i)
            if user.access_project in user.projects:
                user.projects.remove(user.access_project)
            user.access_project = None
            if user.default_project.id == project.id:
                user.default_project = None
        project.users.clear()
        for i in wait_add_users_id_array:
            user = User.query.get(i)
            project.users.append(user)
        for i in wait_to_delete_category_id_array:
            category = Category.query.get(i)
            db.session.delete(category)
        for key, value in exist_categories_id_title_color.items():
            category = Category.query.get(key)
            if category in project.categories:
                if category.title != value['title']:
                    category.title = value['title']
            else:
                new_category = Category(
                    title=value['title'],
                    color=value['color'],
                    project=project
                )
                db.session.add(new_category)
        for i in wait_to_delete_milestone_id_array:
            milestone = Milestone.query.get(i)
            db.session.delete(milestone)
        for key, value in exist_milestones_id_title.items():
            milestone = Milestone.query.get(key)
            if milestone in project.milestones:
                if milestone.title != value:
                    milestone.title = value
            else:
                new_milestone = Milestone(
                    title=value,
                    order=0,
                    project=project
                )
                db.session.add(new_milestone)
        for i in order_id_array:
            title = exist_milestones_id_title[i]
            milestone = Milestone.query.filter_by(title=title).first()
            if milestone:
                milestone.order = str(order)
                order = order + 1
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return 'fail'
    return status
