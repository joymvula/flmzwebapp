from flask import Blueprint, jsonify
from flask_login import login_required
from models import HomeVisit
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/last_visit/<int:child_id>')
@login_required
def last_visit(child_id):
    last = HomeVisit.query.filter_by(child_id=child_id).order_by(HomeVisit.date.desc()).first()
    if not last:
        return jsonify({'last_date': None})
    return jsonify({'last_date': last.date.strftime('%Y-%m-%d')})
