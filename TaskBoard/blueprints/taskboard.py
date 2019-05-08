from flask import Blueprint, render_template, jsonify, abort, request, current_app, send_from_directory, url_for
from flask_login import login_required, current_user
from TaskBoard.models import User, Project, Milestone, Category, Task, Comment, File
from TaskBoard.extensions import db
from datetime import datetime
import uuid, os

taskboard_bp = Blueprint('taskboard', __name__)


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


@taskboard_bp.before_request
@login_required
def login_project():
    pass


@taskboard_bp.route('/')
def index():
    users = User.query.order_by(User.is_admin.desc()).all()
    categories = Category.query.all()
    milestones = Milestone.query.all()
    return render_template('taskboard/board.html', users=users, categories=categories, milestones=milestones)


@taskboard_bp.route('/none-project')
def none_project():
    users = User.query.order_by(User.is_admin.desc()).all()
    return render_template('taskboard/NoProject.html', users=users)


@taskboard_bp.route('/render-milestone-column', methods=['POST'])
def render_milestone_column():
    project_id = request.form.get('project_id', None)
    if project_id != 'None':
        try:
            project = Project.query.get(project_id)
            task_total_count = 0
            task_complete_count = 0
            for milestone in project.milestones:
                task_total_count += len(milestone.tasks)
                for task in milestone.tasks:
                    if task.is_complete:
                        task_complete_count = task_complete_count + 1
                        continue
                    create_date = task.create_time.date()
                    due_date = task.due_date
                    today_date = datetime.utcnow().date()
                    task.task_complete_percent = (today_date - create_date).days * 100 // (due_date - create_date).days
                    if task.task_complete_percent < 33:
                        task.task_process_color = 'green'
                    elif task.task_complete_percent < 67:
                        task.task_process_color = 'orange'
                    elif task.task_complete_percent < 100:
                        task.task_process_color = 'red'
                    elif task.task_complete_percent >= 100:
                        task.is_complete = True
                        db.session.commit()
            complete_percent = 0
            if task_total_count > 0:
                complete_percent = task_complete_count * 100 // task_total_count
            return render_template('taskboard/_MilestoneColumn.html', project=project,
                                   complete_percent=complete_percent)
        except Exception as e:
            print(e)
            abort(500)
    return render_template('taskboard/NoDefaultProject.html')


@taskboard_bp.route('/render-task-column', methods=['POST'])
def render_task_column():
    task_id = request.form.get('task_id', None)
    if task_id:
        try:
            task = Task.query.get(task_id)
            create_date = task.create_time.date()
            due_date = task.due_date
            today_date = datetime.utcnow().date()
            task.task_complete_percent = (today_date - create_date).days * 100 // (due_date - create_date).days
            if task.task_complete_percent < 33:
                task.task_process_color = 'green'
            elif task.task_complete_percent < 67:
                task.task_process_color = 'orange'
            elif task.task_complete_percent < 100:
                task.task_process_color = 'red'
            elif task.task_complete_percent >= 100:
                task.is_complete = True
                db.session.commit()
            return render_template('taskboard/_TaskColumn.html', task=task)
        except Exception as e:
            print(e)
            abort(500)
    return render_template('taskboard/NoTask.html')


@taskboard_bp.route('/save-task-edit-modal', methods=['POST'])
def save_task_edit_modal():
    json_data = request.get_json()
    action_type = json_data.get('action_type', None)
    task_name = json_data.get('task_name', None)
    task_description = json_data.get('task_description', None)
    assigned_user_id = json_data.get('assigned_user_id', None)
    category_id = json_data.get('category_id', None)
    milestone_id = json_data.get('milestone_id', None)
    color_text = json_data.get('color_text', None)
    date_picker_text = json_data.get('date_picker_text', None)
    date_time = datetime.strptime(date_picker_text, '%Y-%m-%d')
    points = json_data.get('points', None)
    try:
        if action_type == 'edit':
            task_id = json_data.get('task_id')
            task = Task.query.get(task_id)
            task.title = task_name.title()
            task.description = task_description
            task.user_id = assigned_user_id
            task.category_id = category_id
            task.milestone_id = milestone_id
            task.color = color_text
            task.due_date = date_time
            task.points = points
        elif action_type == 'add':
            task = Task(title=task_name.title(), description=task_description, user_id=assigned_user_id,
                        category_id=category_id,
                        milestone_id=milestone_id, color=color_text, due_date=date_time, points=points, )
            db.session.add(task)
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return action_type + '-' + str(task.id)


@taskboard_bp.route('/add-milestone-node', methods=['POST'])
def add_milestone_node():
    new_name = request.form.get('new_name', None)
    parent_id = request.form.get('parent_id', None)
    try:
        if parent_id == 'None':
            return 'fail'
        else:
            new_milestone = Milestone(title=new_name.title(), project_id=parent_id)
            db.session.add(new_milestone)
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return 'ok'


@taskboard_bp.route('/rename-node', methods=['POST'])
def rename_node():
    node_type = request.form.get('type')
    node_id = request.form.get('id')
    new_name = request.form.get('new_name').title()
    try:
        if node_type == 'None':
            return 'None'
        elif node_type == 'task':
            task = Task.query.get(node_id)
            task.title = new_name
        elif node_type == 'milestone':
            milestone = Milestone.query.get(node_id)
            milestone.title = new_name
        elif node_type == 'project':
            project = Project.query.get(node_id)
            project.title = new_name
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return 'ok'


@taskboard_bp.route('/copy-node', methods=['POST'])
def copy_node():
    node_type = request.form.get('type')
    node_id = request.form.get('id')
    new_name = request.form.get('new_name').title()
    target_id = request.form.get('target_id')
    try:
        if node_type == 'None':
            return 'None'
        elif node_type == 'task':
            task = Task.query.get(node_id)
            task.title = new_name
            new_task = Task(title=new_name, description=task.description, color=task.color, due_date=task.due_date,
                            points=task.points, milestone_id=target_id, category_id=task.category_id,
                            user_id=task.user_id)
            db.session.add(new_task)
        elif node_type == 'milestone':
            # milestone = Milestone.query.get(node_id)
            new_milestone = Milestone(title=new_name, project_id=target_id)
            db.session.add(new_milestone)
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return 'ok'


@taskboard_bp.route('/move-node', methods=['POST'])
def move_node():
    node_type = request.form.get('type')
    node_id = request.form.get('id')
    # target_id_text = request.form.get('target_id_text')
    target_id = request.form.get('target_id')
    try:
        if node_type == 'None':
            return 'None'
        elif node_type == 'task':
            # target_id = target_id_text.split('milestone_node')[1]
            task = Task.query.get(node_id)
            task.milestone_id = target_id
        elif node_type == 'milestone':
            # target_id = target_id_text.split('project_node')[1]
            milestone = Milestone.query.get(node_id)
            milestone.project_id = target_id
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return 'ok'


@taskboard_bp.route('/delete-node', methods=['POST'])
def delete_node():
    node_type = request.form.get('type')
    node_id = request.form.get('id')
    try:
        if node_type == 'None':
            return 'None'
        elif node_type == 'task':
            wait_delete_obj = Task.query.get(node_id)
        elif node_type == 'milestone':
            wait_delete_obj = Milestone.query.get(node_id)
        elif node_type == 'project':
            wait_delete_obj = Project.query.get(node_id)
        db.session.delete(wait_delete_obj)
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return 'ok'


@taskboard_bp.route('/task-attachment-upload', methods=['POST'])
def task_attachment_upload():
    attachment = request.files.get('attachment')
    task_id = request.form.get('task_id', None)
    user_id = current_user.id
    filename = attachment.filename
    new_filename = random_filename(filename)
    try:
        file = File(source_name=filename, security_name=new_filename, user_id=user_id, task_id=task_id)
        db.session.add(file)
        db.session.commit()
        attachment.save(os.path.join(current_app.config['ATTACHMENT_UPLOAD_PATH'], new_filename))
        response_json = {
            'code': 200,
            'msg': 'ok'
        }
        return jsonify(response_json)
    except Exception as e:
        print(e)
        abort(500)


@taskboard_bp.route('/download-task-attachment/<int:file_id>/<string:filename>')
def download_task_attachment(file_id, filename):
    try:
        file = File.query.get(file_id)
        return send_from_directory(current_app.config['ATTACHMENT_UPLOAD_PATH'], filename, as_attachment=True,
                                   attachment_filename=file.source_name)
    except Exception as e:
        print(e)
        abort(500)


@taskboard_bp.route('/delete-task-attachment', methods=['POST'])
def delete_task_attachment():
    file_id = request.form.get('file_id', None)
    file_security_name = request.form.get('file_security_name', None)
    try:
        file = File.query.get(file_id)
        db.session.delete(file)
        db.session.commit()
        path = os.path.join(current_app.config['ATTACHMENT_UPLOAD_PATH'], file_security_name)
        if os.path.exists(path):
            os.remove(path)
        return 'ok'
    except Exception as e:
        print(e)
        abort(500)


@taskboard_bp.route('/complete-task', methods=['POST'])
def complete_task_by_id():
    task_id = request.form.get('task_id', None)

    if task_id:
        try:
            task = Task.query.get(task_id)
            if task:
                task.is_complete = True
                db.session.commit()
                return 'ok'
        except Exception as e:
            print(e)
            abort(500)
    return 'fail'


@taskboard_bp.route('/edit-or-add-comment', methods=['POST'])
def edit_or_add_comment():
    action = request.form.get('action', None)
    user_id = current_user.id
    text = request.form.get('text', None)
    if action != 'None':
        if action == 'add':
            task_id = request.form.get('task_id', None)
            try:
                comment = Comment(text=text, user_id=user_id, task_id=task_id)
                db.session.add(comment)
                db.session.commit()
                return 'add'
            except Exception as e:
                print(e)
                abort(500)
        elif action == 'edit':
            try:
                comment_id = request.form.get('comment_id', None)
                comment = Comment.query.get(comment_id)
                comment.text = text
                comment.user_id = user_id
                comment.update_time = datetime.utcnow()
                db.session.commit()
                return 'edit'
            except Exception as e:
                print(e)
                abort(500)
    return 'fail'


@taskboard_bp.route('/delete-comment', methods=['POST'])
def delete_comment_by_id():
    comment_id = request.form.get('comment_id', None)
    if not comment_id:
        return 'None'
    try:
        comment = Comment.query.get(comment_id)
        db.session.delete(comment)
        db.session.commit()
    except Exception as e:
        print(e)
        abort(500)
    return 'ok'


@taskboard_bp.route('/tree-json')
def tree_json():
    tree = []
    try:
        if current_user.is_admin:
            projects = Project.query.all()
        else:
            projects = current_user.projects
        for project in projects:
            project_tree = {
                'text': project.title,
                'id': 'project_node' + str(project.id),
                'icon': 'fa fa-pinterest-p',
                'children': [],
                'state': {
                    'opened': True
                },
                'li_attr': {
                    'style': 'font-weight:bold;color:black;font-size:16px',
                }
            }
            for milestone in project.milestones:
                milestone_tree = {
                    'text': milestone.title,
                    'id': 'milestone_node' + str(milestone.id),
                    'icon': 'fa fa-maxcdn',
                    'children': [],
                    'li_attr': {
                        'style': 'font-weight:bold;color:black;font-size:15px',
                    }
                }
                for task in milestone.tasks:
                    task_tree = {
                        'text': task.title,
                        'id': 'task_node' + str(task.id),
                        'icon': 'fa fa-tumblr',
                        'li_attr': {
                            'style': 'font-weight:normal;color:black;font-size:14px;',
                        }
                    }
                    milestone_tree['children'].append(task_tree)
                project_tree['children'].append(milestone_tree)
            tree.append(project_tree)
    except Exception as e:
        print(e)
        abort(500)
    return jsonify(tree)
