"""
Family Logic

Contains all business logic related to family management.
Following the fat logic principle - handles business rules and validation.
"""

from src.models.family_model import Family
from src.models.user_model import User


class FamilyLogic:
    """Business logic for family operations."""
    
    @staticmethod
    def create_family(family_name, creator_id):
        """Create a new family with validation.
        
        Args:
            family_name (str): Name of the family
            creator_id (int): ID of the user creating the family
            
        Returns:
            tuple: (success: bool, family: Family|None, error: str|None)
        """
        # Validate input
        if not family_name or len(family_name.strip()) < 2:
            return False, None, "Family name must be at least 2 characters long"
        
        family_name = family_name.strip()
        
        # Check if user already belongs to a family
        user = User.get_by_id(creator_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id:
            return False, None, "You are already part of a family"
        
        try:
            # Create the family
            family = Family.create_family(family_name, creator_id)
            
            # Add creator to the family
            user.update_family(family.id)
            
            return True, family, None
        except Exception as e:
            return False, None, f"Failed to create family: {str(e)}"
    
    @staticmethod
    def join_family(family_code, user_id):
        """Allow a user to join an existing family.
        
        Args:
            family_code (str): Family code to join
            user_id (int): ID of the user joining
            
        Returns:
            tuple: (success: bool, family: Family|None, error: str|None)
        """
        # Validate input
        if not family_code or len(family_code.strip()) != 6:
            return False, None, "Family code must be 6 characters long"
        
        family_code = family_code.strip().upper()
        
        # Check if user already belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id:
            return False, None, "You are already part of a family"
        
        # Find the family
        family = Family.get_by_code(family_code)
        if not family:
            return False, None, "Invalid family code"
        
        try:
            # Add user to the family
            user.update_family(family.id)
            return True, family, None
        except Exception as e:
            return False, None, f"Failed to join family: {str(e)}"
    
    @staticmethod
    def get_family_info(user_id):
        """Get family information for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            tuple: (family: Family|None, members: list, children: list)
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return None, [], []
        
        family = Family.get_by_id(user.family_id)
        if not family:
            return None, [], []
        
        # Get family members (other parents)
        members = [member for member in family.users if member.id != user_id]
        
        # Get children
        children = family.children
        
        return family, members, children
