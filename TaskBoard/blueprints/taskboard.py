from flask import Blueprint, render_template
from flask_login import login_required

taskboard_bp = Blueprint('taskboard', __name__)


@taskboard_bp.route('/')
@login_required
def index():
    return render_template('taskboard/board.html')
