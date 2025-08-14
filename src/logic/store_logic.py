"""
Store Logic

Contains business logic for family store operations.
"""

from src.models.store_item_model import StoreItem
from src.models.family_points_model import FamilyPoints, PointsTransaction
from src.models.family_model import Family


class StoreLogic:
    """Business logic for store operations."""
    
    @staticmethod
    def create_reward(family_id, name, description, cost, created_by, quantity=None):
        """Create a reward item.
        
        Args:
            family_id (int): ID of the family
            name (str): Name of the reward
            description (str): Description of the reward
            cost (int): Cost in points
            created_by (int): ID of the user creating the item
            quantity (int, optional): Number available (None for infinite)
            
        Returns:
            tuple: (success: bool, item: StoreItem|None, error: str|None)
        """
        try:
            if not name or len(name.strip()) < 1:
                return False, None, "Reward name is required"
            
            if cost < 0:
                return False, None, "Cost cannot be negative"
            
            item = StoreItem.create_item(
                family_id=family_id,
                name=name.strip(),
                description=description.strip() if description else "",
                cost=cost,
                created_by=created_by,
                quantity=quantity,
                item_type='reward'
            )
            return True, item, None
        except Exception as e:
            return False, None, f"Failed to create reward: {str(e)}"
    
    @staticmethod
    def create_coins_to_points_item(family_id, name, description, coins_per_point, created_by):
        """Create a coins-to-points conversion item.
        
        Args:
            family_id (int): ID of the family
            name (str): Name of the conversion item
            description (str): Description
            coins_per_point (int): How many coins equal 1 family point
            created_by (int): ID of the user creating the item
            
        Returns:
            tuple: (success: bool, item: StoreItem|None, error: str|None)
        """
        try:
            if not name or len(name.strip()) < 1:
                return False, None, "Conversion item name is required"
            
            if coins_per_point <= 0:
                return False, None, "Conversion ratio must be positive"
            
            # Coins-to-points items cost the conversion ratio in coins
            # and give 1 family point
            item = StoreItem.create_item(
                family_id=family_id,
                name=name.strip(),
                description=description.strip() if description else "",
                cost=coins_per_point,  # Cost in coins
                created_by=created_by,
                quantity=None,  # Always infinite
                item_type='coins_to_points',
                conversion_ratio=coins_per_point
            )
            return True, item, None
        except Exception as e:
            return False, None, f"Failed to create conversion item: {str(e)}"
    
    @staticmethod
    def purchase_reward(item_id, user_id):
        """Purchase a reward item.
        
        Args:
            item_id (int): ID of the item to purchase
            user_id (int): ID of the user making the purchase
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            item = StoreItem.get_by_id(item_id)
            if not item:
                return False, "Item not found"
            
            if not item.is_available():
                return False, "Item is not available"
            
            # Check if family has enough points
            family_points = FamilyPoints.get_by_family(item.family_id)
            if family_points.total_points < item.cost:
                return False, f"Not enough family points. Need {item.cost}, have {family_points.total_points}"
            
            # Process purchase
            new_total = family_points.subtract_points(item.cost, updated_by=user_id)
            if new_total is None:
                return False, "Transaction failed - insufficient points"
            
            # Update item quantity
            if not item.purchase():
                # Refund points if item purchase failed
                family_points.add_points(item.cost, updated_by=user_id)
                return False, "Item is no longer available"
            
            # Record transaction
            PointsTransaction.create_transaction(
                family_id=item.family_id,
                user_id=user_id,
                amount=-item.cost,
                transaction_type='store_purchase',
                description=f"Purchased: {item.name}",
                reference_id=item.id
            )
            
            return True, f"Successfully purchased {item.name}!"
        except Exception as e:
            return False, f"Purchase failed: {str(e)}"
    
    @staticmethod
    def convert_coins_to_points(item_id, user_id, coins_amount):
        """Convert coins to family points.
        
        Args:
            item_id (int): ID of the conversion item
            user_id (int): ID of the user doing the conversion
            coins_amount (int): Amount of coins to convert
            
        Returns:
            tuple: (success: bool, points_earned: int, message: str)
        """
        try:
            item = StoreItem.get_by_id(item_id)
            if not item or item.item_type != 'coins_to_points':
                return False, 0, "Invalid conversion item"
            
            if not item.is_available():
                return False, 0, "Conversion not available"
            
            if coins_amount <= 0:
                return False, 0, "Coin amount must be positive"
            
            # Calculate points earned
            points_earned = coins_amount // item.conversion_ratio
            if points_earned <= 0:
                return False, 0, f"Not enough coins. Need at least {item.conversion_ratio} coins for 1 point"
            
            # Add points to family pool
            family_points = FamilyPoints.get_by_family(item.family_id)
            family_points.add_points(points_earned, updated_by=user_id)
            
            # Record transaction
            PointsTransaction.create_transaction(
                family_id=item.family_id,
                user_id=user_id,
                amount=points_earned,
                transaction_type='coins_conversion',
                description=f"Converted {coins_amount} coins to {points_earned} points",
                reference_id=item.id
            )
            
            return True, points_earned, f"Converted {coins_amount} coins to {points_earned} family points!"
        except Exception as e:
            return False, 0, f"Conversion failed: {str(e)}"
    
    @staticmethod
    def manually_adjust_points(family_id, amount, user_id, description="Manual adjustment"):
        """Manually adjust family points (adults only).
        
        Args:
            family_id (int): ID of the family
            amount (int): Points to add (positive) or subtract (negative)
            user_id (int): ID of the user making the adjustment
            description (str): Reason for adjustment
            
        Returns:
            tuple: (success: bool, new_total: int, message: str)
        """
        try:
            family_points = FamilyPoints.get_by_family(family_id)
            
            if amount > 0:
                new_total = family_points.add_points(amount, updated_by=user_id)
                action = "added"
            else:
                new_total = family_points.subtract_points(-amount, updated_by=user_id)
                if new_total is None:
                    return False, family_points.total_points, "Cannot subtract more points than available"
                action = "subtracted"
            
            # Record transaction
            PointsTransaction.create_transaction(
                family_id=family_id,
                user_id=user_id,
                amount=amount,
                transaction_type='manual_adjustment',
                description=description
            )
            
            return True, new_total, f"Successfully {action} {abs(amount)} points. Total: {new_total}"
        except Exception as e:
            return False, 0, f"Adjustment failed: {str(e)}"
    
    @staticmethod
    def get_family_store_data(family_id):
        """Get all store data for a family.
        
        Args:
            family_id (int): ID of the family
            
        Returns:
            dict: Store data including items, points, and recent transactions
        """
        try:
            rewards = StoreItem.get_rewards_by_family(family_id)
            conversions = StoreItem.get_conversions_by_family(family_id)
            family_points = FamilyPoints.get_by_family(family_id)
            recent_transactions = PointsTransaction.get_by_family(family_id, limit=10)
            
            return {
                'rewards': rewards,
                'conversions': conversions,
                'family_points': family_points,
                'recent_transactions': recent_transactions
            }
        except Exception as e:
            return {
                'rewards': [],
                'conversions': [],
                'family_points': None,
                'recent_transactions': [],
                'error': str(e)
            }