"""
Store Controller

Family store where parents can add/remove rewards (individual and family rewards).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models.individual_reward_model import IndividualReward
from src.models.family_reward_model import FamilyReward
from src.models.conversion_item_model import ConversionItem
from src.logic.store_logic import StoreLogic, FamilyPointsLogic

store_bp = Blueprint('store', __name__)


@store_bp.route('/store')
@login_required
def index():
    """Display the family store with all rewards."""
    if not current_user.family_id:
        flash('You must be part of a family to access the store.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get all store items for the current family
    store_items = StoreLogic.get_family_store_items(current_user.id)
    family_points = FamilyPointsLogic.get_family_points(current_user.id)
    
    return render_template('private/store/index.html', 
                         individual_rewards=store_items['individual_rewards'],
                         family_rewards=store_items['family_rewards'],
                         conversion_items=store_items['conversion_items'],
                         family_points=family_points)


# Individual Rewards CRUD Operations

@store_bp.route('/store/individual/create', methods=['GET', 'POST'])
@login_required
def create_individual_reward():
    """Create a new individual reward."""
    if not current_user.family_id:
        flash('You must be part of a family to create rewards.', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        coin_cost = request.form.get('coin_cost', type=int)
        qty = request.form.get('qty', type=int, default=1)
        is_infinite = bool(request.form.get('is_infinite'))
        is_available = bool(request.form.get('is_available'))
        
        # Use StoreLogic for validation and creation
        success, reward, error = StoreLogic.create_individual_reward(
            name=name,
            coin_cost=coin_cost,
            user_id=current_user.id,
            description=description or None,
            qty=qty,
            is_infinite=is_infinite
        )
        
        if success:
            flash(f'Individual reward "{reward.name}" created successfully!', 'success')
            return redirect(url_for('store.index'))
        else:
            flash(error, 'error')
    
    return render_template('private/store/create_individual_reward.html')


@store_bp.route('/store/individual/<int:reward_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_individual_reward(reward_id):
    """Edit an existing individual reward."""
    if not current_user.family_id:
        flash('You must be part of a family to edit rewards.', 'warning')
        return redirect(url_for('main.index'))
    
    reward = IndividualReward.get_by_id(reward_id)
    if not reward or reward.family_id != current_user.family_id:
        flash('Reward not found or access denied.', 'error')
        return redirect(url_for('store.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        coin_cost = request.form.get('coin_cost', type=int)
        qty = request.form.get('qty', type=int)
        is_available = bool(request.form.get('is_available'))
        
        # Validation
        if not name:
            flash('Reward name is required.', 'error')
        elif coin_cost is None or coin_cost < 1:
            flash('Coin cost must be a positive number.', 'error')
        elif qty is None or qty < 1:
            flash('Quantity must be a positive number.', 'error')
        else:
            try:
                reward.update(
                    name=name,
                    description=description or None,
                    coin_cost=coin_cost,
                    qty=qty,
                    is_available=is_available
                )
                flash(f'Individual reward "{name}" updated successfully!', 'success')
                return redirect(url_for('store.index'))
            except Exception as e:
                flash('Error updating reward. Please try again.', 'error')
    
    return render_template('private/store/edit_individual_reward.html', reward=reward)


@store_bp.route('/store/individual/<int:reward_id>/delete', methods=['POST'])
@login_required
def delete_individual_reward(reward_id):
    """Delete an individual reward."""
    if not current_user.family_id:
        flash('You must be part of a family to delete rewards.', 'warning')
        return redirect(url_for('main.index'))
    
    reward = IndividualReward.get_by_id(reward_id)
    if not reward or reward.family_id != current_user.family_id:
        flash('Reward not found or access denied.', 'error')
        return redirect(url_for('store.index'))
    
    try:
        reward_name = reward.name
        reward.delete()
        flash(f'Individual reward "{reward_name}" deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting reward. Please try again.', 'error')
    
    return redirect(url_for('store.index'))


# Family Rewards CRUD Operations

@store_bp.route('/store/family/create', methods=['GET', 'POST'])
@login_required
def create_family_reward():
    """Create a new family reward."""
    if not current_user.family_id:
        flash('You must be part of a family to create rewards.', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        point_cost = request.form.get('point_cost', type=int)
        qty = request.form.get('qty', type=int, default=1)
        is_infinite = bool(request.form.get('is_infinite'))
        is_available = bool(request.form.get('is_available'))
        
        # Use StoreLogic for validation and creation
        success, reward, error = StoreLogic.create_family_reward(
            name=name,
            point_cost=point_cost,
            user_id=current_user.id,
            description=description or None,
            qty=qty,
            is_infinite=is_infinite
        )
        
        if success:
            flash(f'Family reward "{reward.name}" created successfully!', 'success')
            return redirect(url_for('store.index'))
        else:
            flash(error, 'error')
    
    return render_template('private/store/create_family_reward.html')


@store_bp.route('/store/family/<int:reward_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_family_reward(reward_id):
    """Edit an existing family reward."""
    if not current_user.family_id:
        flash('You must be part of a family to edit rewards.', 'warning')
        return redirect(url_for('main.index'))
    
    reward = FamilyReward.get_by_id(reward_id)
    if not reward or reward.family_id != current_user.family_id:
        flash('Reward not found or access denied.', 'error')
        return redirect(url_for('store.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        point_cost = request.form.get('point_cost', type=int)
        qty = request.form.get('qty', type=int)
        is_available = bool(request.form.get('is_available'))
        
        # Validation
        if not name:
            flash('Reward name is required.', 'error')
        elif point_cost is None or point_cost < 1:
            flash('Point cost must be a positive number.', 'error')
        elif qty is None or qty < 1:
            flash('Quantity must be a positive number.', 'error')
        else:
            try:
                reward.update(
                    name=name,
                    description=description or None,
                    point_cost=point_cost,
                    qty=qty,
                    is_available=is_available
                )
                flash(f'Family reward "{name}" updated successfully!', 'success')
                return redirect(url_for('store.index'))
            except Exception as e:
                flash('Error updating reward. Please try again.', 'error')
    
    return render_template('private/store/edit_family_reward.html', reward=reward)


@store_bp.route('/store/family/<int:reward_id>/delete', methods=['POST'])
@login_required
def delete_family_reward(reward_id):
    """Delete a family reward."""
    if not current_user.family_id:
        flash('You must be part of a family to delete rewards.', 'warning')
        return redirect(url_for('main.index'))
    
    reward = FamilyReward.get_by_id(reward_id)
    if not reward or reward.family_id != current_user.family_id:
        flash('Reward not found or access denied.', 'error')
        return redirect(url_for('store.index'))
    
    try:
        reward_name = reward.name
        reward.delete()
        flash(f'Family reward "{reward_name}" deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting reward. Please try again.', 'error')
    
    return redirect(url_for('store.index'))


# Conversion Items CRUD Operations

@store_bp.route('/store/conversion/create', methods=['GET', 'POST'])
@login_required
def create_conversion_item():
    """Create a new conversion item."""
    if not current_user.family_id:
        flash('You must be part of a family to create conversion items.', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        coin_cost = request.form.get('coin_cost', type=int)
        points_value = request.form.get('points_value', type=int)
        is_available = bool(request.form.get('is_available'))
        
        # Use StoreLogic for validation and creation
        success, item, error = StoreLogic.create_conversion_item(
            name=name,
            coin_cost=coin_cost,
            points_value=points_value,
            user_id=current_user.id,
            description=description or None
        )
        
        if success:
            flash(f'Conversion item "{item.name}" created successfully!', 'success')
            return redirect(url_for('store.index'))
        else:
            flash(error, 'error')
    
    return render_template('private/store/create_conversion_item.html')


@store_bp.route('/store/conversion/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_conversion_item(item_id):
    """Edit an existing conversion item."""
    if not current_user.family_id:
        flash('You must be part of a family to edit conversion items.', 'warning')
        return redirect(url_for('main.index'))
    
    item = ConversionItem.get_by_id(item_id)
    if not item or item.family_id != current_user.family_id:
        flash('Conversion item not found or access denied.', 'error')
        return redirect(url_for('store.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        coin_cost = request.form.get('coin_cost', type=int)
        points_value = request.form.get('points_value', type=int)
        is_available = bool(request.form.get('is_available'))
        
        # Validation
        if not name:
            flash('Conversion item name is required.', 'error')
        elif coin_cost is None or coin_cost < 1:
            flash('Coin cost must be a positive number.', 'error')
        elif points_value is None or points_value < 1:
            flash('Points value must be a positive number.', 'error')
        else:
            try:
                item.update(
                    name=name,
                    description=description or None,
                    coin_cost=coin_cost,
                    points_value=points_value,
                    is_available=is_available
                )
                flash(f'Conversion item "{name}" updated successfully!', 'success')
                return redirect(url_for('store.index'))
            except Exception as e:
                flash('Error updating conversion item. Please try again.', 'error')
    
    return render_template('private/store/edit_conversion_item.html', item=item)


@store_bp.route('/store/conversion/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_conversion_item(item_id):
    """Delete a conversion item."""
    if not current_user.family_id:
        flash('You must be part of a family to delete conversion items.', 'warning')
        return redirect(url_for('main.index'))
    
    item = ConversionItem.get_by_id(item_id)
    if not item or item.family_id != current_user.family_id:
        flash('Conversion item not found or access denied.', 'error')
        return redirect(url_for('store.index'))
    
    try:
        item_name = item.name
        item.delete()
        flash(f'Conversion item "{item_name}" deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting conversion item. Please try again.', 'error')
    
    return redirect(url_for('store.index'))


@store_bp.route('/store/conversion/<int:item_id>/purchase', methods=['POST'])
@login_required
def purchase_conversion_item(item_id):
    """Purchase a conversion item (convert coins to family points)."""
    if not current_user.family_id:
        flash('You must be part of a family to purchase conversion items.', 'warning')
        return redirect(url_for('main.index'))
    
    success, message, error = StoreLogic.purchase_conversion_item(item_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('store.index'))


# Family Points Management

@store_bp.route('/store/family-points/adjust', methods=['POST'])
@login_required
def adjust_family_points():
    """Manually adjust family points."""
    if not current_user.family_id:
        flash('You must be part of a family to adjust family points.', 'warning')
        return redirect(url_for('main.index'))
    
    adjustment = request.form.get('adjustment', type=int)
    if adjustment is None or adjustment == 0:
        flash('Please enter a valid adjustment amount.', 'error')
        return redirect(url_for('store.index'))
    
    success, new_total, error = FamilyPointsLogic.adjust_family_points(
        current_user.family_id, adjustment, current_user.id
    )
    
    if success:
        action = "added" if adjustment > 0 else "subtracted"
        flash(f'Successfully {action} {abs(adjustment)} family points! New total: {new_total}', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('store.index'))


@store_bp.route('/store/family-points/set', methods=['POST'])
@login_required
def set_family_points():
    """Set family points to a specific value."""
    if not current_user.family_id:
        flash('You must be part of a family to set family points.', 'warning')
        return redirect(url_for('main.index'))
    
    new_total = request.form.get('new_total', type=int)
    if new_total is None or new_total < 0:
        flash('Please enter a valid non-negative number.', 'error')
        return redirect(url_for('store.index'))
    
    success, final_total, error = FamilyPointsLogic.set_family_points(
        current_user.family_id, new_total, current_user.id
    )
    
    if success:
        flash(f'Family points set to {final_total}!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('store.index'))
