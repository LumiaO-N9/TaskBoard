from flask import Blueprint, render_template
from flask_login import login_required
from TaskBoard.models import Log
from datetime import datetime, date, timedelta
import collections

timeline_bp = Blueprint('timeline', __name__)


@timeline_bp.before_request
@login_required
def login_project():
    pass


@timeline_bp.route('/<int:week>')
def index(week):
    today = date.today() - timedelta(days=week * 7)
    last_log = Log.query.order_by(Log.create_time).first()
    week_logs_dict = collections.OrderedDict()
    last_week = week + 1
    if not last_log:
        last_week = -1
        week = 0
    else:
        for i in range(7):
            date_tmp = today - timedelta(days=i)
            if datetime.combine(date_tmp, datetime.min.time()) < last_log.create_time:
                last_week = -1
            start = datetime(date_tmp.year, date_tmp.month, date_tmp.day, 0, 0, 0)
            end = datetime(date_tmp.year, date_tmp.month, date_tmp.day, 23, 59, 50)
            logs = Log.query.filter(Log.create_time >= start).filter(Log.create_time <= end).order_by(
                Log.create_time.desc()).all()
            week_logs_dict[start.strftime('%m月%d日')] = logs
    return render_template('timeline/timeline.html', week_logs_dict=week_logs_dict, last_week=last_week,
                           before_week=week - 1)
