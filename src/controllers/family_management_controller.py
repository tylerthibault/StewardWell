"""
Family Management Controller

Allows family managers to view and approve/reject pending join requests.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_required, current_user
from src.models.family_model import Family
from src.models.join_request_model import JoinRequest
from src.models.user_model import User
from src.models.child_model import Child

family_mgmt_bp = Blueprint('family_mgmt', __name__)


@family_mgmt_bp.route('/family-management')
@login_required
def index():
    # Must be in a family and be the creator/manager
    family = Family.get_by_id(current_user.family_id) if current_user.family_id else None
    if not family:
        flash('Join or create a family to manage members.', 'error')
        return redirect(url_for('main.dashboard'))
    is_manager = current_user.id == family.creator_id
    pending = JoinRequest.get_pending_by_family(family.id) if is_manager else []
    members = family.users if family else []
    children = family.children if family else []
    return render_template('private/family_management/index.html', family=family, members=members, children=children, pending=pending, is_manager=is_manager)


@family_mgmt_bp.route('/family-management/invite-adult', methods=['POST'])
@login_required
def invite_adult():
    family = Family.get_by_id(current_user.family_id) if current_user.family_id else None
    if not family:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    if current_user.id != family.creator_id:
        flash('Only the family manager can invite adults.', 'error')
        return redirect(url_for('family_mgmt.index'))

    identifier = request.form.get('identifier', '').strip()
    if not identifier:
        flash('Please provide a username or email to invite.', 'error')
        return redirect(url_for('family_mgmt.index'))

    # Find user by username first, then email
    user = User.get_by_username(identifier) or User.get_by_email(identifier.lower())
    if not user:
        flash('No user found with that username/email. Ask them to register and use the family code.', 'error')
        return redirect(url_for('family_mgmt.index'))
    if user.family_id:
        flash('That user already belongs to a family.', 'error')
        return redirect(url_for('family_mgmt.index'))

    JoinRequest.create_request(user.id, family.id)
    flash('Invitation sent (pending approval).', 'success')
    return redirect(url_for('family_mgmt.index'))


@family_mgmt_bp.route('/family-management/impersonate/child/<int:child_id>', methods=['POST'])
@login_required
def impersonate_child(child_id: int):
    child = Child.query.get_or_404(child_id)
    family = Family.get_by_id(current_user.family_id) if current_user.family_id else None
    if not family or child.family_id != family.id:
        abort(403)
    session['impersonating_child_id'] = child.id
    flash(f'Viewing as {child.name}.', 'success')
    return redirect(url_for('kids.dashboard'))


@family_mgmt_bp.route('/family-management/stop-impersonating')
@login_required
def stop_impersonating():
    session.pop('impersonating_child_id', None)
    flash('Returned to parent view.', 'info')
    return redirect(url_for('family_mgmt.index'))


@family_mgmt_bp.route('/family-management/approve/<int:req_id>')
@login_required
def approve(req_id: int):
    req = JoinRequest.query.get(req_id)
    if not req:
        flash('Request not found', 'error')
        return redirect(url_for('family_mgmt.index'))
    family = Family.get_by_id(req.family_id)
    if current_user.id != (family.creator_id if family else None):
        flash('Only the family manager can approve requests', 'error')
        return redirect(url_for('family_mgmt.index'))
    if req.approve():
        flash('Request approved', 'success')
    else:
        flash('Unable to approve request', 'error')
    return redirect(url_for('family_mgmt.index'))


@family_mgmt_bp.route('/family-management/reject/<int:req_id>')
@login_required
def reject(req_id: int):
    req = JoinRequest.query.get(req_id)
    if not req:
        flash('Request not found', 'error')
        return redirect(url_for('family_mgmt.index'))
    family = Family.get_by_id(req.family_id)
    if current_user.id != (family.creator_id if family else None):
        flash('Only the family manager can reject requests', 'error')
        return redirect(url_for('family_mgmt.index'))
    if req.reject():
        flash('Request rejected', 'success')
    else:
        flash('Unable to reject request', 'error')
    return redirect(url_for('family_mgmt.index'))
