from datetime import datetime
from TaskBoard.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

association_table = db.Table('association', db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                             db.Column('project_id', db.Integer, db.ForeignKey('project.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(254))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_time = db.Column(db.DateTime, default=datetime.utcnow)
    default_project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    access_project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    default_project = db.relationship('Project', back_populates='default_users', foreign_keys=[default_project_id])
    access_project = db.relationship('Project', back_populates='access_users', foreign_keys=[access_project_id])
    projects = db.relationship('Project', secondary=association_table, back_populates='users')
    tasks = db.relationship('Task', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    status = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    default_users = db.relationship('User', back_populates='default_project', foreign_keys='User.default_project_id')
    access_users = db.relationship('User', back_populates='access_project', foreign_keys='User.access_project_id')
    users = db.relationship('User', secondary=association_table, back_populates='projects')
    milestones = db.relationship('Milestone', back_populates='project', cascade='all,delete-orphan')
    categories = db.relationship('Category', back_populates='project', cascade='all,delete-orphan')


class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    order = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', back_populates='milestones')
    tasks = db.relationship('Task', back_populates='milestone', cascade='all,delete-orphan')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    description = db.Column(db.Text)
    color = db.Column(db.String(30), default='#fff5ee')
    due_date = db.Column(db.Date)
    points = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    milestone = db.relationship('Milestone', back_populates='tasks')
    category = db.relationship('Category', back_populates='tasks')
    user = db.relationship('User', back_populates='tasks')
    comments = db.relationship('Comment', back_populates='task')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    color = db.Column(db.String(30), default='#d9edf7')
    project = db.relationship('Project', back_populates='categories')
    tasks = db.relationship('Task', back_populates='category')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    is_edited = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='comments')
    task = db.relationship('Task', back_populates='comments')
