"""
Authentication Controller

Handles user authentication routes (login, register, logout).
Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from src.logic.auth_logic import AuthLogic

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Process registration through business logic
        success, user, error = AuthLogic.register_user(username, email, password)
        
        if success:
            login_user(user)
            flash('Registration successful! Welcome to StewardWell.', 'success')
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
