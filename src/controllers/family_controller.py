"""
Family Controller

Handles family management routes (create, join family).
Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.logic.family_logic import FamilyLogic

family_bp = Blueprint('family', __name__)


@family_bp.route('/create_family', methods=['POST'])
@login_required
def create_family():
    """Handle family creation."""
    family_name = request.form.get('family_name', '').strip()
    
    # Process family creation through business logic
    success, family, error = FamilyLogic.create_family(family_name, current_user.id)
    
    if success:
        flash(f'Family "{family.name}" created! Family code: {family.family_code}', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('main.dashboard'))


@family_bp.route('/join_family', methods=['POST'])
@login_required
def join_family():
    """Handle joining an existing family."""
    family_code = request.form.get('family_code', '').strip()
    
    # Process family join through business logic
    success, family, error = FamilyLogic.join_family(family_code, current_user.id)
    
    if success:
        flash(f'Successfully joined "{family.name}"!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('main.dashboard'))
