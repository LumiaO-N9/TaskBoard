from flask import Flask, render_template
from TaskBoard.settings import config
from TaskBoard.extensions import db, login_manager, csrf, bootstrap
from TaskBoard.blueprints import auth, taskboard, setting
from TaskBoard.models import User, Project, Milestone, Category, Task
from flask_wtf.csrf import CSRFError
import os, click


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('TaskBoard')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_shell_context(app)
    register_commands(app)
    return app


def register_logging(app):
    pass  # print Application logs


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    app.register_blueprint(taskboard.taskboard_bp)
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(setting.setting_bp, url_prefix='/setting')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Project=Project, Milestone=Milestone, Category=Category, Task=Task)


def register_template_context(app):
    pass


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--project', default=3, help='Quantity of projects, default is 3.')
    @click.option('--user', default=10, help='Quantity of users, default is 10.')
    @click.option('--milestone', default=5, help='Quantity of milestones, default is 5.')
    @click.option('--category', default=4, help='Quantity of categories, default is 4.')
    @click.option('--task', default=4, help='Quantity of tasks, default is 4.')
    def forge(project, user, milestone, category, task):
        """Generate fake data."""
        from TaskBoard.fakes import fake_admin_user, fake_Projects, fake_Users, fake_milestones, fake_categories, \
            fake_tasks
        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin_user()

        click.echo('Generating %d projects...' % project)
        fake_Projects(project)

        click.echo('Generating %d users...' % user)
        fake_Users(user)

        click.echo('Generating %d milestones...' % milestone)
        fake_milestones(milestone)

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d tasks...' % task)
        fake_tasks(task)

        click.echo('Done.')
