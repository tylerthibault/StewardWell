"""
Store Controller

Family store where parents can add/remove rewards (individual and family rewards).
"""

from flask import Blueprint, render_template
from flask_login import login_required

store_bp = Blueprint('store', __name__)


@store_bp.route('/store')
@login_required
def index():
    return render_template('private/store/index.html')
