from TaskBoard.models import User, Project, Milestone, Task, Category, Comment
from TaskBoard.extensions import db
from faker import Faker
from random import choice
import random

fake = Faker()


def fake_Projects(count=3):
    for i in range(count):
        project = Project(
            title=fake.word()
        )
        db.session.add(project)
    db.session.commit()


def fake_admin_user():
    user = User(
        username='admin',
        is_admin=True,
        email=fake.email(),
    )
    user.set_password('TaskBoard')
    db.session.add(user)
    db.session.commit()


def fake_Users(count=10):
    for i in range(count):
        user = User(
            username='worker%d' % i,
            default_project=Project.query.get(random.randint(1, Project.query.count())),
            access_project=Project.query.get(random.randint(1, Project.query.count())),
            email='10000%d@example.com' % i,
        )
        user.set_password('TaskBoard')
        if user.access_project == user.default_project:
            user.projects.append(user.access_project)
        else:
            user.projects.append(user.default_project)
            user.projects.append(user.access_project)
        db.session.add(user)
    db.session.commit()


def fake_milestones(count=5):
    for i in range(Project.query.count()):  # 为每个project创建count-1或者count个Milestone
        for j in range(random.randint(count - 1, count)):
            milestone = Milestone(
                title=fake.word(),
                order=j,
                project=Project.query.get(i + 1)
            )
            db.session.add(milestone)
    db.session.commit()


def fake_categories(count=4):
    for i in range(Project.query.count()):  # 为每个project创建count-2或者count个Category
        for j in range(random.randint(count - 2, count)):
            category = Category(
                title=fake.name(),
                project=Project.query.get(i + 1)
            )
            db.session.add(category)
    db.session.commit()


def fake_tasks(count=4):
    for i in range(Milestone.query.count()):  # 为每个Milestone创建0~count个task
        for j in range(random.randint(0, count)):
            task = Task(
                title=fake.name(),
                description=fake.text(166),
                due_date=fake.date_this_year(before_today=False, after_today=True),
                points=random.randint(0, 10),
                milestone=Milestone.query.get(i + 1)
            )
            task.category = choice(task.milestone.project.categories)
            task.user = choice(task.milestone.project.users)
            db.session.add(task)
    db.session.commit()


def fake_comments(count=3):
    for i in range(Task.query.count()):  # 为每个Task创建0~count个comment
        for j in range(random.randint(0, count)):
            comment = Comment(
                text=fake.text(100),
                task_id=Task.query.get(i + 1).id
            )
            comment.user_id = choice(User.query.all()).id
            db.session.add(comment)
    db.session.commit()
