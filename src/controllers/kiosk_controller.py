"""
Kiosk Controller

Handles kiosk mode routes — an always-on, touch-friendly display for children
to check their chore boards and coin balances without accessing the parent dashboard.

Following the thin controller principle - minimal request/response handling.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import desc

from src.models.child_model import Child
from src.models.chore_model import Chore
from src.models.family_model import Family

kiosk_bp = Blueprint('kiosk', __name__, url_prefix='/kiosk')


def _get_family():
    """Retrieve the current user's family.

    Returns:
        Family or None: Family object if found, None otherwise.
    """
    if not getattr(current_user, 'family_id', None):
        return None
    return Family.get_by_id(current_user.family_id)


@kiosk_bp.route('/', methods=['GET'])
@login_required
def idle():
    """Display the kiosk idle / home screen.

    Shows all children with their coin balances, family points, and recent
    activity.  Works even if kiosk_mode is not set so parents can preview.
    """
    family = _get_family()
    children = Child.get_by_family(current_user.family_id) if family else []
    family_points = family.family_points if family else 0

    # Recent activity: completed chores (last 10) as a simple name list
    recent_activity = []
    if family:
        recent_chores = (
            Chore.query
            .filter_by(family_id=family.id, status='completed')
            .order_by(desc(Chore.updated_at))
            .limit(10)
            .all()
        )
        recent_activity = [c.name for c in recent_chores]

    return render_template(
        'kiosk/idle.html',
        family=family,
        children=children,
        family_points=family_points,
        recent_activity=recent_activity,
        kiosk_mode=session.get('kiosk_mode', False),
    )


@kiosk_bp.route('/enter', methods=['POST'])
@login_required
def enter():
    """Activate kiosk mode and redirect to the idle screen."""
    session['kiosk_mode'] = True
    return redirect(url_for('kiosk.idle'))


@kiosk_bp.route('/select', methods=['GET'])
@login_required
def select():
    """Show the child selector screen.

    Displays all children as large touch targets so a child can identify
    themselves before entering their PIN.
    """
    family = _get_family()
    children = Child.get_by_family(current_user.family_id) if family else []
    return render_template('kiosk/select.html', children=children, family=family)


@kiosk_bp.route('/pin', methods=['GET', 'POST'])
@login_required
def pin():
    """Show the PIN entry screen or verify a submitted PIN.

    GET  — render the PIN pad for the selected child.
    POST — validate the PIN; on success redirect to the child board.
           If the child has no PIN yet, the first 4-digit input sets it
           (first-time setup flow).
    """
    child_id = request.args.get('child_id') or request.form.get('child_id')
    child = Child.get_by_id(int(child_id)) if child_id else None

    if not child:
        flash('Child not found.', 'error')
        return redirect(url_for('kiosk.select'))

    error = None
    if request.method == 'POST':
        submitted_pin = request.form.get('pin', '').strip()

        if child.pin is None:
            # First-time setup: any 4-digit input becomes the PIN
            if len(submitted_pin) == 4 and submitted_pin.isdigit():
                child.set_pin(submitted_pin)
                session['kiosk_child_id'] = child.id
                return redirect(url_for('kiosk.child_board'))
            else:
                error = 'Please enter a 4-digit PIN to set up your account.'
        else:
            if submitted_pin == child.pin:
                session['kiosk_child_id'] = child.id
                return redirect(url_for('kiosk.child_board'))
            else:
                error = 'Incorrect PIN. Please try again.'

    return render_template('kiosk/pin.html', child=child, error=error)


@kiosk_bp.route('/child', methods=['GET'])
@login_required
def child_board():
    """Display the child's personal chore board.

    Requires session['kiosk_child_id'] to be set (i.e. PIN was verified).
    """
    child_id = session.get('kiosk_child_id')
    if not child_id:
        return redirect(url_for('kiosk.select'))

    child = Child.get_by_id(child_id)
    if not child:
        session.pop('kiosk_child_id', None)
        return redirect(url_for('kiosk.select'))

    pending_chores = [
        c for c in Chore.get_by_child(child_id)
        if c.status == 'pending'
    ]

    return render_template('kiosk/child_board.html', child=child, chores=pending_chores)


@kiosk_bp.route('/child/done', methods=['POST'])
@login_required
def child_done():
    """Mark the child's session as complete and return to the idle screen.

    Clears the active child from the session so the display resets to the
    family idle view.
    """
    session.pop('kiosk_child_id', None)
    return redirect(url_for('kiosk.idle'))


@kiosk_bp.route('/exit', methods=['GET', 'POST'])
@login_required
def exit_kiosk():
    """Show or handle the parent-password exit form.

    GET  — render the password verification form.
    POST — verify the parent's password; on success clear kiosk session keys
           and redirect to the main dashboard.
    """
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if current_user.check_password(password):
            session.pop('kiosk_mode', None)
            session.pop('kiosk_child_id', None)
            return redirect(url_for('main.dashboard'))
        else:
            error = 'Incorrect password. Please try again.'

    return render_template('kiosk/exit.html', error=error)
