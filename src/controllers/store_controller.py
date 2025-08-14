"""
Store Controller

Family store where parents can add/remove rewards (individual and family rewards).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models.individual_reward_model import IndividualReward
from src.models.family_reward_model import FamilyReward

store_bp = Blueprint('store', __name__)


@store_bp.route('/store')
@login_required
def index():
    """Display the family store with all rewards."""
    if not current_user.family_id:
        flash('You must be part of a family to access the store.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get all rewards for the current family
    individual_rewards = IndividualReward.get_by_family(current_user.family_id)
    family_rewards = FamilyReward.get_by_family(current_user.family_id)
    
    return render_template('private/store/index.html', 
                         individual_rewards=individual_rewards,
                         family_rewards=family_rewards)


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
                IndividualReward.create_reward(
                    name=name,
                    description=description or None,
                    coin_cost=coin_cost,
                    qty=qty,
                    is_available=is_available,
                    family_id=current_user.family_id,
                    created_by=current_user.id
                )
                flash(f'Individual reward "{name}" created successfully!', 'success')
                return redirect(url_for('store.index'))
            except Exception as e:
                flash('Error creating reward. Please try again.', 'error')
    
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
                FamilyReward.create_reward(
                    name=name,
                    description=description or None,
                    point_cost=point_cost,
                    qty=qty,
                    is_available=is_available,
                    family_id=current_user.family_id,
                    created_by=current_user.id
                )
                flash(f'Family reward "{name}" created successfully!', 'success')
                return redirect(url_for('store.index'))
            except Exception as e:
                flash('Error creating reward. Please try again.', 'error')
    
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
