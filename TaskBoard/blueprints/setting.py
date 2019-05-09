from flask import Blueprint, render_template, request, current_app
from TaskBoard.models import Project, User, Milestone, Category, Tag, Log
from TaskBoard.extensions import db
from flask_login import login_required, current_user
import os

setting_bp = Blueprint('setting', __name__)


def create_log(log, flag=True, color='#666'):
    if flag:
        new_log = Log(log=current_user.username + ' ' + log, color=color)
    else:
        new_log = Log(log=log, color=color)
    db.session.add(new_log)


@setting_bp.before_request
@login_required
def login_project():
    pass


@setting_bp.route('/')
def index():
    projects = Project.query.order_by(Project.title).all()
    users = User.query.order_by(User.is_admin.desc()).all()
    tags = Tag.query.all()
    return render_template('setting/settings.html', projects=projects, users=users, tags=tags)


@setting_bp.route('/change-default-project', methods=['POST'])
def change_default_project():
    project_id = request.form['project_id']
    try:
        user = current_user
        project = Project.query.get(project_id)
        if user.default_project != project:
            user.default_project = project
            create_log('change default project to ' + project.title)
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
        create_log('change his or her password. ')
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
            create_log('change his or her email to ' + info)
        elif name == 'username':
            if info != current_user.username and User.query.filter_by(username=info).first():
                return 'same'
            create_log('change his or her username to ' + info)
            current_user.username = info
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return 'fail'
    return 'ok'


@setting_bp.route('/chang-project-status', methods=['POST'])
def change_project_status():
    project_id = request.form.get('project_id', None)
    if not project_id:
        return 'None'
    try:
        project = Project.query.get(project_id)
        status = project.status
        project.status = not status
        action = 'Inactive'
        if project.status:
            action = 'Active'
        create_log(action.title() + ' project ' + project.title)
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
    user_id = request.form.get('user_id', None)
    if not user_id:
        return 'None'
    try:
        user = User.query.get(user_id)
        db.session.delete(user)
        create_log('remove user ' + current_user.username, color='#F66B68')
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/del-project-by-id', methods=['POST'])
def del_project_by_id():
    project_id = request.form.get('project_id', None)
    if not project_id:
        return 'None'
    try:
        project = Project.query.get(project_id)
        for milestone in project.milestones:
            for task in milestone.tasks:
                upload_path = current_app.config['ATTACHMENT_UPLOAD_PATH']
                for file in task.files:
                    file_path = os.path.join(upload_path, file.security_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        create_log('Delete file ' + file.source_name + ' (auto)', False, color='#F66B68')
                for comment in task.comments:
                    create_log('Delete comment ' + comment.text[:20] + '...... (auto)', False, color='#F66B68')
                create_log('Delete task ' + task.title + '(auto)', False, color='#F66B68')
            create_log(' Delete milestone ' + milestone.title + ' (auto)', False, color='#F66B68')
        create_log('delete project ' + project.title, color='#F66B68')
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
    tag_id = request.form.get('tag', None)
    default_project_id = request.form.get('default_project', None)
    access_project_id = request.form.get('access_project', None)
    is_admin = request.form.get('is_admin', False)
    status = 'edit'
    try:
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return 'None'
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
        if tag_id:
            if tag_id == 'None':
                user.tag_id = None
            else:
                user.tag_id = tag_id
        if default_project_id:
            if default_project_id == 'None':
                user.default_project_id = None
            else:
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
        if status == 'edit':
            create_log('edit user ' + user.username + '\'s information')
        elif status == 'add':
            create_log('create user ' + user.username, color='#008000')
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


@setting_bp.route('/add-tag', methods=['POST'])
def add_tag():
    tag = request.form.get('tag', None)
    if not tag:
        return 'None'
    try:
        if Tag.query.filter_by(tag=tag).first():
            return 'same'
        new_tag = Tag(tag=tag)
        db.session.add(new_tag)
        create_log('add tag ' + tag.tag)
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/edit-tag', methods=['POST'])
def edit_tag():
    tag_id = request.form.get('tag_id', None)
    tag_tag = request.form.get('tag', None)
    if not tag_tag or not tag_id:
        return 'None'
    try:
        same_tag = Tag.query.filter_by(tag=tag_tag).first()
        if same_tag and same_tag.id != tag_id:
            return 'same'
        tag = Tag.query.get(tag_id)
        create_log('rename tag ' + tag.tag + ' to ' + tag_tag)
        tag.tag = tag_tag
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/delete-tag', methods=['POST'])
def delete_tag():
    tag_id = request.form.get('tag_id', None)
    if not tag_id:
        return 'None'
    try:
        tag = Tag.query.get(tag_id)
        create_log('delete tag ' + tag.tag, color='#F66B68')
        db.session.delete(tag)
        db.session.commit()
    except Exception as e:
        print(e)
        return 'fail'
    return 'ok'


@setting_bp.route('/save-project-edit-modal', methods=["POST"])
def save_project_edit_modal():
    json_data = request.get_json()
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
    project_users_original = []
    try:
        if project_id:
            project = Project.query.get(project_id)
        else:
            project = Project()
            status = 'add'
            db.session.add(project)
        for user in project.users:
            project_users_original.append(user)
        if status == 'edit':
            create_log('edit project ' + project.title)
        if project.title != project_title:
            project.title = project_title
            if status == 'edit':
                create_log('rename project ' + project.title + ' to ' + project_title)
            elif status == 'add':
                create_log('create new project ' + project_title)
        for i in wait_remove_users_id_array:
            user = User.query.get(i)
            if user.access_project in user.projects:
                user.projects.remove(user.access_project)
            user.access_project = None
            create_log(
                'remove user ' + user.username + ' from project ' + project.title + '\'workers')
            if user.default_project and user.default_project.id == project.id:
                user.default_project = None
        project.users.clear()
        for i in wait_add_users_id_array:
            user = User.query.get(i)
            project.users.append(user)
            if user not in project_users_original:
                create_log(
                    'add user ' + user.username + ' to project ' + project.title + '\'s workers')
        for i in wait_to_delete_category_id_array:
            category = Category.query.get(i)
            create_log('delete category ' + category.title + ' in project ' + project.title, color='#F66B68')
            db.session.delete(category)
        for key, value in exist_categories_id_title_color.items():
            category = Category.query.get(key)
            if category in project.categories:
                if category.title != value['title']:
                    create_log('rename category ' + category.title + ' to ' + value['title'])
                    category.title = value['title']
                if category.color != value['color']:
                    create_log('change category ' + category.title + '\'s color to ' + value['color'])
                    category.color = value['color']
            else:
                new_category = Category(
                    title=value['title'],
                    color=value['color'],
                    project=project
                )
                create_log(
                    'create category ' + new_category.title + ' for project ' + project.title + ' and set its color as ' + new_category.color)
                db.session.add(new_category)
        for i in wait_to_delete_milestone_id_array:
            milestone = Milestone.query.get(i)
            create_log('delete milestone ' + milestone.title + ' from project ' + project.title + '\'s milestones',
                       color='#F66B68')
            db.session.delete(milestone)
        for key, value in exist_milestones_id_title.items():
            milestone = Milestone.query.get(key)
            if milestone in project.milestones:
                if milestone.title != value:
                    create_log('rename milestone ' + milestone.title + ' to ' + value)
                    milestone.title = value.title()
            else:
                new_milestone = Milestone(
                    title=value.title(),
                    order=0,
                    project=project
                )
                create_log('create milestone ' + new_milestone.title.title() + ' for project ' + project.title)
                db.session.add(new_milestone)
        project_milestones_order_original = [milestone.id for milestone in project.milestones]
        for i in order_id_array:
            title = exist_milestones_id_title[i]
            milestone = Milestone.query.filter_by(title=title.title()).first()
            if milestone:
                milestone.order = order
                order = order + 1
        db.session.commit()
        project_milestones_order_present = [milestone.id for milestone in project.milestones]
        if project_milestones_order_original != project_milestones_order_present:
            create_log('change the order of milestones in project ' + project.title + ' : ' + ' '.join(
                [milestone.title for milestone in project.milestones]))
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return 'fail'
    return status
