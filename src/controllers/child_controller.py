"""
Child Controller

Handles child management routes (add, remove children).
Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.logic.child_logic import ChildLogic

child_bp = Blueprint('child', __name__)


@child_bp.route('/add_child', methods=['POST'])
@login_required
def add_child():
    """Handle adding a child to the family."""
    name = request.form.get('child_name', '').strip()
    age = request.form.get('child_age', '')
    
    # Convert age to int if provided, otherwise None
    age_int = None
    if age and age.strip():
        try:
            age_int = int(age.strip())
        except ValueError:
            flash('Age must be a valid number', 'error')
            return redirect(url_for('main.dashboard'))
    
    # Process child addition through business logic
    success, child, error = ChildLogic.add_child(name, current_user.id, age_int)
    
    if success:
        flash(f'Child "{child.name}" added to the family!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('main.dashboard'))


@child_bp.route('/delete_child/<int:child_id>')
@login_required
def delete_child(child_id):
    """Handle removing a child from the family."""
    # Process child removal through business logic
    success, error = ChildLogic.remove_child(child_id, current_user.id)
    
    if success:
        flash('Child removed from the family', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('main.dashboard'))
