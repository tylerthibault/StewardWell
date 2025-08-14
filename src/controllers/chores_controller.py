"""
Chores Controller

Chore center to add/remove chores and assign them to family members (including adults).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.logic.chore_logic import ChoreLogic
from src.models.family_model import Family
from src.models.child_model import Child
from src.models.user_model import User

chores_bp = Blueprint('chores', __name__)


@chores_bp.route('/chores')
@login_required
def index():
    """Display the chore center."""
    if not current_user.family_id:
        flash('Join or create a family to access chores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        family = Family.get_by_id(current_user.family_id)
        is_manager = family and current_user.id == family.creator_id
        
        # Get chores summary
        chores_summary = ChoreLogic.get_family_chores_summary(current_user.family_id)
        
        # Get available chores for current user
        available_chores = ChoreLogic.get_available_chores_for_adult(current_user.family_id, current_user.id)
        
        # Get family members for assignment options
        family_members = family.users if family else []
        children = family.children if family else []
        
        return render_template('private/chores/index.html',
                             family=family,
                             is_manager=is_manager,
                             chores_summary=chores_summary,
                             available_chores=available_chores,
                             family_members=family_members,
                             children=children)
    except Exception as e:
        flash(f'Error loading chores: {str(e)}', 'error')
        return render_template('private/chores/index.html',
                             family=None,
                             is_manager=False,
                             chores_summary={'pending': [], 'completed': []},
                             available_chores=[],
                             family_members=[],
                             children=[])


@chores_bp.route('/chores/create', methods=['POST'])
@login_required
def create_chore():
    """Create a new chore."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    points_reward = request.form.get('points_reward', type=int) or 0
    assigned_to_type = request.form.get('assigned_to_type', 'any')
    assigned_to_id = request.form.get('assigned_to_id')
    
    # Convert assigned_to_id to int if provided
    if assigned_to_id and assigned_to_id != '':
        try:
            assigned_to_id = int(assigned_to_id)
        except ValueError:
            assigned_to_id = None
    else:
        assigned_to_id = None
    
    success, chore, error = ChoreLogic.create_chore(
        family_id=current_user.family_id,
        name=name,
        description=description,
        points_reward=points_reward,
        assigned_to_type=assigned_to_type,
        created_by=current_user.id,
        assigned_to_id=assigned_to_id
    )
    
    if success:
        flash(f'Chore "{name}" created successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('chores.index'))


@chores_bp.route('/chores/complete/<int:chore_id>', methods=['POST'])
@login_required
def complete_chore(chore_id):
    """Complete a chore."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    success, points_earned, message = ChoreLogic.complete_chore(
        chore_id=chore_id,
        completed_by_type='adult',
        completed_by_id=current_user.id
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('chores.index'))


@chores_bp.route('/chores/complete-for-child/<int:chore_id>/<int:child_id>', methods=['POST'])
@login_required
def complete_chore_for_child(chore_id, child_id):
    """Complete a chore on behalf of a child (parents only)."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Verify child belongs to family
    child = Child.get_by_id(child_id)
    if not child or child.family_id != current_user.family_id:
        flash('Invalid child selection.', 'error')
        return redirect(url_for('chores.index'))
    
    success, points_earned, message = ChoreLogic.complete_chore(
        chore_id=chore_id,
        completed_by_type='child',
        completed_by_id=child_id
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('chores.index'))


@chores_bp.route('/chores/delete/<int:chore_id>', methods=['POST'])
@login_required
def delete_chore(chore_id):
    """Delete/archive a chore."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    success, message = ChoreLogic.delete_chore(chore_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('chores.index'))


@chores_bp.route('/chores/child/<int:child_id>')
@login_required
def child_chores(child_id):
    """View chores for a specific child."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Verify child belongs to family
    child = Child.get_by_id(child_id)
    if not child or child.family_id != current_user.family_id:
        flash('Invalid child selection.', 'error')
        return redirect(url_for('chores.index'))
    
    try:
        available_chores = ChoreLogic.get_available_chores_for_child(current_user.family_id, child_id)
        
        return render_template('private/chores/child_chores.html',
                             child=child,
                             available_chores=available_chores)
    except Exception as e:
        flash(f'Error loading child chores: {str(e)}', 'error')
        return redirect(url_for('chores.index'))
