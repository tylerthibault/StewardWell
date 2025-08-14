"""
Chores Controller

Chore center to add/remove chores and assign them to family members (including adults).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from src.logic.chore_logic import ChoreLogic
from src.logic.child_logic import ChildLogic
from src.logic.family_logic import FamilyLogic

chores_bp = Blueprint('chores', __name__)


@chores_bp.route('/chores')
@login_required
def index():
    """Display all chores for the user's family."""
    # Get query parameters for filtering
    status = request.args.get('status')
    child_id = request.args.get('child_id', type=int)
    
    # Get chores with optional filtering
    chores = ChoreLogic.get_family_chores(current_user.id, status=status, child_id=child_id)
    
    # Get children for filter dropdown
    children = ChildLogic.get_family_children(current_user.id)
    
    return render_template('private/chores/index.html', 
                         chores=chores, 
                         children=children,
                         current_status=status,
                         current_child_id=child_id)


@chores_bp.route('/chores/new')
@login_required
def new():
    """Display form to create a new chore."""
    children = ChildLogic.get_family_children(current_user.id)
    family_members = ChoreLogic.get_family_members(current_user.id)
    return render_template('private/chores/new.html', children=children, family_members=family_members)


@chores_bp.route('/chores', methods=['POST'])
@login_required
def create():
    """Create a new chore."""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    coin_amount = request.form.get('coin_amount', 0)
    point_amount = request.form.get('point_amount', 0)
    is_recurring = request.form.get('is_recurring') == 'on'
    assigned_child_id = request.form.get('assigned_child_id')
    assigned_user_id = request.form.get('assigned_user_id')
    notes = request.form.get('notes', '').strip()
    priority = request.form.get('priority', 'medium')
    
    # Parse due date
    due_date = None
    due_date_str = request.form.get('due_date')
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    # Parse recurring days
    recurring_days = []
    if is_recurring:
        for day in range(7):
            if request.form.get(f'recurring_day_{day}') == 'on':
                recurring_days.append(day)
    
    # Convert empty strings to None for optional fields
    description = description if description else None
    notes = notes if notes else None
    assigned_child_id = int(assigned_child_id) if assigned_child_id else None
    assigned_user_id = int(assigned_user_id) if assigned_user_id else None
    
    success, chore, error = ChoreLogic.create_chore(
        name=name,
        user_id=current_user.id,
        description=description,
        coin_amount=coin_amount,
        point_amount=point_amount,
        is_recurring=is_recurring,
        recurring_days=recurring_days if recurring_days else None,
        assigned_child_id=assigned_child_id,
        assigned_user_id=assigned_user_id,
        due_date=due_date,
        notes=notes,
        priority=priority
    )
    
    if success:
        flash(f'Chore "{chore.name}" created successfully!', 'success')
        return redirect(url_for('chores.index'))
    else:
        flash(error, 'error')
        children = ChildLogic.get_family_children(current_user.id)
        family_members = ChoreLogic.get_family_members(current_user.id)
        return render_template('private/chores/new.html', 
                             children=children,
                             family_members=family_members,
                             form_data=request.form)


@chores_bp.route('/chores/<int:chore_id>')
@login_required
def show(chore_id):
    """Display individual chore details."""
    chores = ChoreLogic.get_family_chores(current_user.id)
    chore = next((c for c in chores if c.id == chore_id), None)
    
    if not chore:
        flash('Chore not found', 'error')
        return redirect(url_for('chores.index'))
    
    # Get children for assignment dropdown
    children = ChildLogic.get_family_children(current_user.id)
    family_members = ChoreLogic.get_family_members(current_user.id)
    
    return render_template('private/chores/show.html', chore=chore, children=children, family_members=family_members)


@chores_bp.route('/chores/<int:chore_id>/edit')
@login_required
def edit(chore_id):
    """Display form to edit a chore."""
    chores = ChoreLogic.get_family_chores(current_user.id)
    chore = next((c for c in chores if c.id == chore_id), None)
    
    if not chore:
        flash('Chore not found', 'error')
        return redirect(url_for('chores.index'))
    
    children = ChildLogic.get_family_children(current_user.id)
    family_members = ChoreLogic.get_family_members(current_user.id)
    return render_template('private/chores/edit.html', chore=chore, children=children, family_members=family_members)


@chores_bp.route('/chores/<int:chore_id>', methods=['POST', 'PUT'])
@login_required
def update(chore_id):
    """Update a chore."""
    # Parse form data
    updates = {}
    
    if 'name' in request.form:
        updates['name'] = request.form.get('name', '').strip()
    
    if 'description' in request.form:
        description = request.form.get('description', '').strip()
        updates['description'] = description if description else None
    
    if 'coin_amount' in request.form:
        updates['coin_amount'] = request.form.get('coin_amount', 0)
    
    if 'point_amount' in request.form:
        updates['point_amount'] = request.form.get('point_amount', 0)
    
    if 'is_recurring' in request.form:
        updates['is_recurring'] = request.form.get('is_recurring') == 'on'
    
    if 'assigned_child_id' in request.form:
        assigned_child_id = request.form.get('assigned_child_id')
        updates['assigned_child_id'] = int(assigned_child_id) if assigned_child_id else None
    
    if 'assigned_user_id' in request.form:
        assigned_user_id = request.form.get('assigned_user_id')
        updates['assigned_user_id'] = int(assigned_user_id) if assigned_user_id else None
    
    if 'notes' in request.form:
        notes = request.form.get('notes', '').strip()
        updates['notes'] = notes if notes else None
    
    if 'priority' in request.form:
        updates['priority'] = request.form.get('priority', 'medium')
    
    # Parse due date
    if 'due_date' in request.form:
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                updates['due_date'] = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                updates['due_date'] = None
        else:
            updates['due_date'] = None
    
    # Parse recurring days
    if updates.get('is_recurring'):
        recurring_days = []
        for day in range(7):
            if request.form.get(f'recurring_day_{day}') == 'on':
                recurring_days.append(day)
        updates['recurring_days'] = recurring_days if recurring_days else None
    else:
        updates['recurring_days'] = None
    
    success, chore, error = ChoreLogic.update_chore(chore_id, current_user.id, **updates)
    
    if success:
        flash(f'Chore "{chore.name}" updated successfully!', 'success')
        return redirect(url_for('chores.show', chore_id=chore_id))
    else:
        flash(error, 'error')
        return redirect(url_for('chores.edit', chore_id=chore_id))


@chores_bp.route('/chores/<int:chore_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete(chore_id):
    """Delete a chore."""
    success, error = ChoreLogic.delete_chore(chore_id, current_user.id)
    
    if success:
        flash('Chore deleted successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('chores.index'))


@chores_bp.route('/chores/<int:chore_id>/assign', methods=['POST'])
@login_required
def assign(chore_id):
    """Assign a chore to a child or user."""
    child_id = request.form.get('child_id')
    user_id = request.form.get('user_id')
    
    if not child_id and not user_id:
        flash('Please select a child or family member to assign the chore to', 'error')
        return redirect(url_for('chores.show', chore_id=chore_id))
    
    if child_id and user_id:
        flash('Please select either a child OR a family member, not both', 'error')
        return redirect(url_for('chores.show', chore_id=chore_id))
    
    if child_id:
        success, chore, error = ChoreLogic.assign_chore_to_child(chore_id, int(child_id), current_user.id)
    else:
        success, chore, error = ChoreLogic.assign_chore_to_user(chore_id, int(user_id), current_user.id)
    
    if success:
        flash(f'Chore assigned successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('chores.show', chore_id=chore_id))


@chores_bp.route('/chores/<int:chore_id>/complete', methods=['POST'])
@login_required
def complete(chore_id):
    """Mark a chore as completed."""
    success, chore, error = ChoreLogic.complete_chore(chore_id, current_user.id)
    
    if success:
        flash(f'Chore completed! Earned {chore.coin_amount} coins and {chore.point_amount} family points!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('chores.show', chore_id=chore_id))


@chores_bp.route('/api/chores')
@login_required
def api_chores():
    """API endpoint to get chores as JSON."""
    status = request.args.get('status')
    child_id = request.args.get('child_id', type=int)
    
    chores = ChoreLogic.get_family_chores(current_user.id, status=status, child_id=child_id)
    
    return jsonify({
        'chores': [chore.to_dict() for chore in chores]
    })
