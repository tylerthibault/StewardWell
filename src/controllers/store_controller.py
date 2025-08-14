"""
Store Controller

Family store to manage rewards, coins-to-points conversion, and family points.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.logic.store_logic import StoreLogic
from src.models.family_model import Family

store_bp = Blueprint('store', __name__)


@store_bp.route('/store')
@login_required
def index():
    """Display the family store."""
    if not current_user.family_id:
        flash('Join or create a family to access the store.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        store_data = StoreLogic.get_family_store_data(current_user.family_id)
        family = Family.get_by_id(current_user.family_id)
        is_manager = family and current_user.id == family.creator_id
        
        return render_template('private/store/index.html', 
                             store_data=store_data,
                             family=family,
                             is_manager=is_manager)
    except Exception as e:
        flash(f'Error loading store: {str(e)}', 'error')
        return render_template('private/store/index.html',
                             store_data={'rewards': [], 'conversions': [], 'family_points': None, 'recent_transactions': []},
                             family=None,
                             is_manager=False)


@store_bp.route('/store/create-reward', methods=['POST'])
@login_required
def create_reward():
    """Create a new reward item."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if user is family manager
    family = Family.get_by_id(current_user.family_id)
    if not family or current_user.id != family.creator_id:
        flash('Only the family manager can create rewards.', 'error')
        return redirect(url_for('store.index'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    cost = request.form.get('cost', type=int)
    quantity_str = request.form.get('quantity', '').strip()
    
    # Handle infinite quantity
    quantity = None if quantity_str == '' or quantity_str.lower() == 'infinite' else int(quantity_str) if quantity_str.isdigit() else None
    
    success, item, error = StoreLogic.create_reward(
        family_id=current_user.family_id,
        name=name,
        description=description,
        cost=cost,
        created_by=current_user.id,
        quantity=quantity
    )
    
    if success:
        flash(f'Reward "{name}" created successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('store.index'))


@store_bp.route('/store/create-conversion', methods=['POST'])
@login_required
def create_conversion():
    """Create a coins-to-points conversion item."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if user is family manager
    family = Family.get_by_id(current_user.family_id)
    if not family or current_user.id != family.creator_id:
        flash('Only the family manager can create conversion items.', 'error')
        return redirect(url_for('store.index'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    coins_per_point = request.form.get('coins_per_point', type=int)
    
    success, item, error = StoreLogic.create_coins_to_points_item(
        family_id=current_user.family_id,
        name=name,
        description=description,
        coins_per_point=coins_per_point,
        created_by=current_user.id
    )
    
    if success:
        flash(f'Conversion item "{name}" created successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('store.index'))


@store_bp.route('/store/purchase/<int:item_id>', methods=['POST'])
@login_required
def purchase_item(item_id):
    """Purchase a reward item."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    success, message = StoreLogic.purchase_reward(item_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('store.index'))


@store_bp.route('/store/convert-coins/<int:item_id>', methods=['POST'])
@login_required
def convert_coins(item_id):
    """Convert coins to family points."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    coins_amount = request.form.get('coins_amount', type=int)
    if not coins_amount or coins_amount <= 0:
        flash('Please enter a valid number of coins.', 'error')
        return redirect(url_for('store.index'))
    
    success, points_earned, message = StoreLogic.convert_coins_to_points(item_id, current_user.id, coins_amount)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('store.index'))


@store_bp.route('/store/adjust-points', methods=['POST'])
@login_required
def adjust_points():
    """Manually adjust family points (managers only)."""
    if not current_user.family_id:
        flash('Join or create a family first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if user is family manager
    family = Family.get_by_id(current_user.family_id)
    if not family or current_user.id != family.creator_id:
        flash('Only the family manager can manually adjust points.', 'error')
        return redirect(url_for('store.index'))
    
    amount = request.form.get('amount', type=int)
    description = request.form.get('description', '').strip() or "Manual adjustment"
    
    if amount == 0:
        flash('Please enter a non-zero amount.', 'error')
        return redirect(url_for('store.index'))
    
    success, new_total, message = StoreLogic.manually_adjust_points(
        family_id=current_user.family_id,
        amount=amount,
        user_id=current_user.id,
        description=description
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('store.index'))