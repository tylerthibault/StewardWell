"""
Authentication Controller

Handles user authentication routes (login, register, logout).
Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from src.logic.auth_logic import AuthLogic
from src.logic.family_logic import FamilyLogic

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        family_code = request.form.get('family_code', '').strip().upper()
        
        # Process registration through business logic
        success, user, error = AuthLogic.register_user(username, email, password)
        
        if success:
            login_user(user)
            # Attempt to join a family immediately if a code was provided
            if family_code:
                joined, family, join_error = FamilyLogic.join_family(family_code, user.id)
                if joined:
                    flash(f'Registration successful! You joined "{family.name}".', 'success')
                else:
                    # Still allow login; user can create/join from dashboard later
                    flash(join_error or 'Could not join family with that code.', 'error')
                    flash('Registration successful! You can create or join a family from your dashboard.', 'info')
            else:
                flash('Registration successful! Create or join a family from your dashboard.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(error, 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('public/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Process login through business logic
        success, user, error = AuthLogic.authenticate_user(username, password)
        
        if success:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(error, 'error')
    
    return render_template('public/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))
