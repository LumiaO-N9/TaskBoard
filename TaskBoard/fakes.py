from TaskBoard.models import User, Project, Milestone, Task, Category, Comment, Tag, Log
from TaskBoard.extensions import db
from faker import Faker
from random import choice
import random

fake = Faker()

color_array = ['#dff0d8', '#d9edf7', '#fcf8e3', '#f2dede']


# '#ffffff', '#337ab7', '#5cb85c', '#5bc0de', '#f0ad4e', '#d9534f']


def fake_Projects(count=3):
    for i in range(count):
        project = Project(
            title=fake.word().title(),
            create_time=fake.date_time_between(start_date="-37d", end_date="-35d", tzinfo=None)
        )
        log = Log(log='Create Project ' + project.title)
        log.create_time = project.create_time
        db.session.add(project)
        db.session.add(log)
    db.session.commit()


def fake_admin_user():
    user = User(
        username='admin',
        is_admin=True,
        email=fake.email(),
        create_time=fake.date_time_between(start_date="-35d", end_date="-35d", tzinfo=None)
    )
    user.set_password('TaskBoard.')
    log = Log(log='Create Admin User')
    log.create_time = user.create_time
    db.session.add(user)
    db.session.add(log)
    db.session.commit()


def fake_Tags(count=8):
    for i in range(count):
        tag = Tag(tag=fake.word().title(),
                  create_time=fake.date_time_between(start_date="-34d", end_date="-34d", tzinfo=None)
                  )
        log = Log(log='Create Tag: ' + tag.tag)
        log.create_time = tag.create_time
        db.session.add(tag)
        db.session.add(log)
    db.session.commit()


def fake_Users(count=10):
    for i in range(count):
        user = User(
            username='worker%d' % i,
            default_project=Project.query.get(random.randint(1, Project.query.count())),
            access_project=Project.query.get(random.randint(1, Project.query.count())),
            email='10000%d@example.com' % i,
            create_time=fake.date_time_between(start_date="-34d", end_date="-2d", tzinfo=None)
        )
        user.tag_id = random.randint(1, Tag.query.count())
        user.set_password('TaskBoard.')
        if user.access_project == user.default_project:
            user.projects.append(user.access_project)
        else:
            user.projects.append(user.default_project)
            user.projects.append(user.access_project)
        log = Log(log='Create User ' + user.username)
        log.create_time = user.create_time
        db.session.add(log)
        db.session.add(user)
    db.session.commit()


def fake_milestones(count=5):
    for i in range(Project.query.count()):  # 为每个project创建count-1或者count个Milestone
        # for j in range(random.randint(count - 1, count)):
        for j in range(count):  # generate five Milestones for every Project
            milestone = Milestone(
                title=fake.word().title(),
                order=j,
                project=Project.query.get(i + 1),
                create_time=fake.date_time_between(start_date="-35d", end_date="-30d", tzinfo=None)
            )
            log = Log(log='Create Milestone ' + milestone.title + ' in Project ' + milestone.project.title)
            log.create_time = milestone.create_time
            db.session.add(milestone)
            db.session.add(log)
    db.session.commit()


def fake_categories(count=4):
    for i in range(Project.query.count()):  # 为每个project创建count-2或者count个Category
        # for j in range(random.randint(count - 2, count)):
        for j in range(count):  # generate four categories for every project
            category = Category(
                title=fake.name(),
                project=Project.query.get(i + 1),
                color=choice(color_array),
                create_time=fake.date_time_between(start_date="-35d", end_date="-30d", tzinfo=None)
            )
            log = Log(log='Create Category ' + category.title + ' for Project ' + category.project.title)
            log.create_time = category.create_time
            db.session.add(log)
            db.session.add(category)
    db.session.commit()


def fake_tasks(count=4):
    for i in range(Milestone.query.count()):  # 为每个Milestone创建0~count个task
        # for j in range(random.randint(0, count)):
        for j in range(count):  # generate four tasks for every milestone
            task = Task(
                title=fake.name(),
                description=fake.text(166),
                color=choice(color_array),
                # due_date=fake.date_this_year(before_today=False, after_today=True),
                due_date=fake.date_this_month(before_today=False, after_today=True),
                # create_time=fake.past_datetime(start_date='-30d'),
                create_time=fake.date_time_between(start_date='-30d', end_date="-2d",
                                                   tzinfo=None),
                points=random.randint(0, 10),
                milestone=Milestone.query.get(i + 1)
            )
            task.is_complete = choice([False, True, False])
            task.category = choice(task.milestone.project.categories)
            task.user = choice(task.milestone.project.users)
            log = Log(log='Create Task ' + task.title + ' in Milestone ' + task.milestone.title)
            log.create_time = task.create_time
            db.session.add(log)
            db.session.add(task)
    db.session.commit()


def fake_comments(count=3):
    for i in range(Task.query.count()):  # 为每个Task创建0~count个comment
        # for j in range(random.randint(0, count)):
        for j in range(count):  # generate three comments for every task
            comment = Comment(
                text=fake.text(100),
                task=Task.query.get(i + 1)
            )
            comment.user_id = choice(User.query.all()).id
            comment.create_time = fake.date_time_between(start_date=comment.task.create_time, end_date="-1d",
                                                         tzinfo=None)
            log = Log(log='Create Comment for Task ' + comment.task.title)
            log.create_time = comment.create_time
            db.session.add(log)
            db.session.add(comment)
    db.session.commit()
