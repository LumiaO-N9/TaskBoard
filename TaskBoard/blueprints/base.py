from flask import Blueprint, render_template
from flask_login import login_required
from TaskBoard.extensions import socketio
from flask_socketio import emit

base_bp = Blueprint('base', __name__)


@socketio.on('refresh')
def auto_refresh():
    emit('refresh', 'refresh', broadcast=True)


@base_bp.before_request
@login_required
def login_project():
    pass


@base_bp.route('/get-js')
def get_js():
    return render_template('base.min.js')
