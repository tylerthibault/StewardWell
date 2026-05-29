"""
Main Controller

Handles main application routes like landing page and dashboard.
Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.logic.family_logic import FamilyLogic
from src.logic.child_logic import ChildLogic
from src.models.chore_model import Chore

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    """Display the landing page."""
    return render_template('public/landing/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Display the user dashboard with family information."""
    try:
        # Get family information
        family, members, children = FamilyLogic.get_family_info(current_user.id)

        # Pending approval count
        pending_approvals = 0
        if current_user.family_id:
            pending_approvals = Chore.query.filter_by(
                family_id=current_user.family_id, status='submitted'
            ).count()

        return render_template('private/dashboard/index.html',
                             family=family,
                             members=members,
                             children=children,
                             pending_approvals=pending_approvals)
    except Exception as e:
        # Log the error in production
        print(f"Dashboard error: {e}")
        return render_template('private/dashboard/index.html',
                             family=None,
                             members=[],
                             children=[],
                             pending_approvals=0)