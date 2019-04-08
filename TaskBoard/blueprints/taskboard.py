from flask import Blueprint, render_template, jsonify, abort, request
from flask_login import login_required, current_user
from TaskBoard.models import User, Project, Milestone, Category, Task, Comment
from TaskBoard.extensions import db
from datetime import datetime

taskboard_bp = Blueprint('taskboard', __name__)


@taskboard_bp.before_request
@login_required
def login_project():
    pass


@taskboard_bp.route('/')
def index():
    return render_template('taskboard/board.html')


@taskboard_bp.route('/render-milestone-column', methods=['POST'])
def render_milestone_column():
    project_id = request.form.get('project_id', None)
    if project_id != 'None':
        try:
            project = Project.query.get(project_id)
            return render_template('taskboard/_MilestoneColumn.html', project=project)
        except Exception as e:
            print(e)
            abort(500)
    return render_template('taskboard/NoDefaultProject.html')


@taskboard_bp.route('/render-task-column', methods=['POST'])
def render_task_column():
    task_id = request.form.get('task_id', None)
    if task_id != 'None':
        try:
            task = Task.query.get(task_id)
            return render_template('taskboard/_TaskColumn.html', task=task)
        except Exception as e:
            print(e)
            abort(500)
    return render_template('taskboard/NoDefaultProject.html')


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
                'children': [],
                'state': {
                    'opened': True
                },
                'li_attr': {
                    'class': 'text-capitalize',
                    'style': 'font-weight:bold;color:black;font-size:16px',
                }
            }
            for milestone in project.milestones:
                milestone_tree = {
                    'text': milestone.title,
                    'id': 'milestone_node' + str(milestone.id),
                    'children': [],
                    'li_attr': {
                        'style': 'font-weight:bold;color:black;font-size:15px',
                    }
                }
                for task in milestone.tasks:
                    task_tree = {
                        'text': task.title,
                        'id': 'task_node' + str(task.id),
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
