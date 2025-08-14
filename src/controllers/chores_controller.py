"""
Chores Controller

Chore center to add/remove chores and assign them to family members (including adults).
"""

from flask import Blueprint, render_template
from flask_login import login_required

chores_bp = Blueprint('chores', __name__)


@chores_bp.route('/chores')
@login_required
def index():
    return render_template('private/chores/index.html')
