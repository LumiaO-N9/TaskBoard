from flask import Blueprint, render_template, jsonify, abort, request, current_app, send_from_directory, url_for
from flask_login import login_required, current_user
from TaskBoard.models import User, Project, Milestone, Category, Task, Comment, File
from TaskBoard.extensions import db
from datetime import datetime
import uuid, os

statistic_bp = Blueprint('statistic', __name__)


@statistic_bp.before_request
@login_required
def login_project():
    pass


@statistic_bp.route('/')
def index():
    return render_template('statistic/statistic.html')
