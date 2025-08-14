"""
Kids Controller (Impersonation View)

Allows a logged-in parent to temporarily view a simplified child dashboard.
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.child_model import Child
from src.models.chore_model import Chore
from src.logic.chore_logic import ChoreLogic

kids_bp = Blueprint('kids', __name__, url_prefix='/kids')


@kids_bp.get('/dashboard')
@login_required
def dashboard():
    child_id = session.get('impersonating_child_id')
    if not child_id:
        flash('Start child view from Family Management.', 'info')
        return redirect(url_for('family_mgmt.index'))
    child = Child.query.get(child_id)
    if not child or not current_user.family_id or child.family_id != current_user.family_id:
        session.pop('impersonating_child_id', None)
        flash('Child view expired or forbidden.', 'warning')
        return redirect(url_for('family_mgmt.index'))
    chores = Chore.get_by_child(child.id)
    pending = [c for c in chores if getattr(c, 'status', 'pending') == 'pending']
    submitted = [c for c in chores if getattr(c, 'status', '') == 'submitted']
    completed = [c for c in chores if getattr(c, 'status', '') == 'completed']
    return render_template('child/dashboard/index.html', child=child, pending_chores=pending, submitted_chores=submitted, completed_chores=completed)


@kids_bp.post('/chores/<int:chore_id>/submit')
@login_required
def submit_chore(chore_id: int):
    """Child submits a chore for adult review."""
    child_id = session.get('impersonating_child_id')
    if not child_id:
        flash('Start child view from Family Management.', 'info')
        return redirect(url_for('family_mgmt.index'))
    child = Child.query.get(child_id)
    if not child or not current_user.family_id or child.family_id != current_user.family_id:
        session.pop('impersonating_child_id', None)
        flash('Child view expired or forbidden.', 'warning')
        return redirect(url_for('family_mgmt.index'))

    chore = Chore.get_by_id(chore_id)
    if not chore or chore.family_id != current_user.family_id or chore.assigned_child_id != child.id:
        flash('Chore not found for this child.', 'error')
        return redirect(url_for('kids.dashboard'))

    success, chore, error = ChoreLogic.submit_chore(chore_id, child.id, current_user.id)
    if success:
        flash('Submitted for review! A parent will check it soon.', 'success')
    else:
        flash(error or 'Could not submit chore.', 'error')
    return redirect(url_for('kids.dashboard'))
