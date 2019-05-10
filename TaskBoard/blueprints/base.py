from flask import Blueprint, render_template
from flask_login import login_required

base_bp = Blueprint('base', __name__)


@base_bp.before_request
@login_required
def login_project():
    pass


@base_bp.route('/get-js')
def get_js():
    return render_template('base.min.js')
