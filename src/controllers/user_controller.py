"""
User Controller

Handles user profile management routes.
Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.logic.user_logic import UserLogic

user_bp = Blueprint('user', __name__)


@user_bp.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    """Handle editing user profile."""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    
    # Process profile update through business logic
    success, user, error = UserLogic.update_user_profile(
        current_user.id,
        username if username else None,
        email if email else None
    )
    
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('main.dashboard'))