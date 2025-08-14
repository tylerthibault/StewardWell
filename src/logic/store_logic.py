"""
Store Logic

Contains all business logic related to store operations.
Following the fat logic principle - handles business rules and validation.
"""

from src.models.individual_reward_model import IndividualReward
from src.models.family_reward_model import FamilyReward
from src.models.conversion_item_model import ConversionItem
from src.models.family_model import Family
from src.models.user_model import User


class StoreLogic:
    """Business logic for store operations."""
    
    @staticmethod
    def create_individual_reward(name, coin_cost, user_id, description=None, qty=1, is_infinite=False):
        """Create a new individual reward with validation.
        
        Args:
            name (str): Name of the reward
            coin_cost (int): Cost in coins
            user_id (int): ID of the user creating the reward
            description (str, optional): Description of the reward
            qty (int, optional): Quantity available
            is_infinite (bool, optional): Whether the reward has infinite quantity
            
        Returns:
            tuple: (success: bool, reward: IndividualReward|None, error: str|None)
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return False, None, "Reward name must be at least 2 characters long"
        
        if coin_cost is None or coin_cost < 1:
            return False, None, "Coin cost must be a positive number"
        
        if not is_infinite and (qty is None or qty < 1):
            return False, None, "Quantity must be a positive number unless infinite"
        
        # Check if user belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if not user.family_id:
            return False, None, "You must be part of a family to create rewards"
        
        try:
            reward = IndividualReward.create_reward(
                name=name.strip(),
                coin_cost=coin_cost,
                family_id=user.family_id,
                created_by=user_id,
                description=description,
                qty=qty if not is_infinite else 1,  # qty is ignored for infinite items
                is_infinite=is_infinite
            )
            return True, reward, None
        except Exception as e:
            return False, None, f"Failed to create reward: {str(e)}"
    
    @staticmethod
    def create_family_reward(name, point_cost, user_id, description=None, qty=1, is_infinite=False):
        """Create a new family reward with validation.
        
        Args:
            name (str): Name of the reward
            point_cost (int): Cost in points
            user_id (int): ID of the user creating the reward
            description (str, optional): Description of the reward
            qty (int, optional): Quantity available
            is_infinite (bool, optional): Whether the reward has infinite quantity
            
        Returns:
            tuple: (success: bool, reward: FamilyReward|None, error: str|None)
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return False, None, "Reward name must be at least 2 characters long"
        
        if point_cost is None or point_cost < 1:
            return False, None, "Point cost must be a positive number"
        
        if not is_infinite and (qty is None or qty < 1):
            return False, None, "Quantity must be a positive number unless infinite"
        
        # Check if user belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if not user.family_id:
            return False, None, "You must be part of a family to create rewards"
        
        try:
            reward = FamilyReward.create_reward(
                name=name.strip(),
                point_cost=point_cost,
                family_id=user.family_id,
                created_by=user_id,
                description=description,
                qty=qty if not is_infinite else 1,  # qty is ignored for infinite items
                is_infinite=is_infinite
            )
            return True, reward, None
        except Exception as e:
            return False, None, f"Failed to create reward: {str(e)}"
    
    @staticmethod
    def create_conversion_item(name, coin_cost, points_value, user_id, description=None):
        """Create a new conversion item with validation.
        
        Args:
            name (str): Name of the conversion item
            coin_cost (int): Cost in coins
            points_value (int): Points received for conversion
            user_id (int): ID of the user creating the item
            description (str, optional): Description of the item
            
        Returns:
            tuple: (success: bool, item: ConversionItem|None, error: str|None)
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return False, None, "Conversion item name must be at least 2 characters long"
        
        if coin_cost is None or coin_cost < 1:
            return False, None, "Coin cost must be a positive number"
        
        if points_value is None or points_value < 1:
            return False, None, "Points value must be a positive number"
        
        # Check if user belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if not user.family_id:
            return False, None, "You must be part of a family to create conversion items"
        
        try:
            item = ConversionItem.create_item(
                name=name.strip(),
                coin_cost=coin_cost,
                points_value=points_value,
                family_id=user.family_id,
                created_by=user_id,
                description=description
            )
            return True, item, None
        except Exception as e:
            return False, None, f"Failed to create conversion item: {str(e)}"
    
    @staticmethod
    def get_family_store_items(user_id):
        """Get all store items for a user's family.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            dict: Dictionary containing all store items
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return {
                'individual_rewards': [],
                'family_rewards': [],
                'conversion_items': []
            }
        
        return {
            'individual_rewards': IndividualReward.get_by_family(user.family_id),
            'family_rewards': FamilyReward.get_by_family(user.family_id),
            'conversion_items': ConversionItem.get_by_family(user.family_id)
        }
    
    @staticmethod
    def purchase_conversion_item(item_id, user_id):
        """Process a conversion item purchase (convert coins to family points).
        
        Args:
            item_id (int): ID of the conversion item
            user_id (int): ID of the user making the purchase
            
        Returns:
            tuple: (success: bool, message: str|None, error: str|None)
        """
        # Get the conversion item
        item = ConversionItem.get_by_id(item_id)
        if not item:
            return False, None, "Conversion item not found"
        
        # Get the user
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        # Verify user belongs to the same family
        if user.family_id != item.family_id:
            return False, None, "You can only purchase items from your own family store"
        
        # Check if item is available
        if not item.is_available:
            return False, None, "This conversion item is not available"
        
        # Get the family
        family = Family.get_by_id(user.family_id)
        if not family:
            return False, None, "Family not found"
        
        # Note: In a real implementation, we would check if the user has enough coins
        # and subtract the coins from their account. For now, we'll just add the points.
        
        try:
            # Add points to family pool
            family.add_points(item.points_value)
            
            return True, f"Successfully converted {item.coin_cost} coins to {item.points_value} family points!", None
        except Exception as e:
            return False, None, f"Failed to process conversion: {str(e)}"


class FamilyPointsLogic:
    """Business logic for family points management."""
    
    @staticmethod
    def adjust_family_points(family_id, points_adjustment, user_id):
        """Manually adjust family points (add or subtract).
        
        Args:
            family_id (int): ID of the family
            points_adjustment (int): Points to add (positive) or subtract (negative)
            user_id (int): ID of the user making the adjustment
            
        Returns:
            tuple: (success: bool, new_total: int|None, error: str|None)
        """
        # Validate user belongs to the family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id != family_id:
            return False, None, "You can only adjust points for your own family"
        
        # Get the family
        family = Family.get_by_id(family_id)
        if not family:
            return False, None, "Family not found"
        
        try:
            if points_adjustment > 0:
                family.add_points(points_adjustment)
            elif points_adjustment < 0:
                if not family.subtract_points(abs(points_adjustment)):
                    return False, None, "Insufficient family points for this adjustment"
            
            return True, family.family_points, None
        except Exception as e:
            return False, None, f"Failed to adjust family points: {str(e)}"
    
    @staticmethod
    def set_family_points(family_id, new_total, user_id):
        """Set family points to a specific value.
        
        Args:
            family_id (int): ID of the family
            new_total (int): New total points value
            user_id (int): ID of the user making the change
            
        Returns:
            tuple: (success: bool, new_total: int|None, error: str|None)
        """
        # Validate input
        if new_total < 0:
            return False, None, "Family points cannot be negative"
        
        # Validate user belongs to the family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id != family_id:
            return False, None, "You can only set points for your own family"
        
        # Get the family
        family = Family.get_by_id(family_id)
        if not family:
            return False, None, "Family not found"
        
        try:
            family.set_points(new_total)
            return True, family.family_points, None
        except Exception as e:
            return False, None, f"Failed to set family points: {str(e)}"
    
    @staticmethod
    def get_family_points(user_id):
        """Get the current family points for a user's family.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            int: Current family points (0 if no family)
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return 0
        
        family = Family.get_by_id(user.family_id)
        if not family:
            return 0
        
        return family.family_points