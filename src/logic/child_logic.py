"""
Child Logic

Contains all business logic related to child management.
Following the fat logic principle - handles business rules and validation.
"""

from src.models.child_model import Child
from src.models.user_model import User


class ChildLogic:
    """Business logic for child operations."""
    
    @staticmethod
    def add_child(name, user_id, age=None):
        """Add a new child to the user's family.
        
        Args:
            name (str): Name of the child
            user_id (int): ID of the user adding the child
            age (int, optional): Age of the child
            
        Returns:
            tuple: (success: bool, child: Child|None, error: str|None)
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return False, None, "Child name must be at least 2 characters long"
        
        name = name.strip()
        
        # Validate age if provided
        if age is not None:
            try:
                age = int(age)
                if age < 0 or age > 18:
                    return False, None, "Age must be between 0 and 18"
            except (ValueError, TypeError):
                return False, None, "Age must be a valid number"
        
        # Check if user belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if not user.family_id:
            return False, None, "You must be part of a family to add children"
        
        try:
            # Create the child
            child = Child.create_child(name, user.family_id, user_id, age)
            return True, child, None
        except Exception as e:
            return False, None, f"Failed to add child: {str(e)}"
    
    @staticmethod
    def remove_child(child_id, user_id):
        """Remove a child from the family.
        
        Args:
            child_id (int): ID of the child to remove
            user_id (int): ID of the user requesting removal
            
        Returns:
            tuple: (success: bool, error: str|None)
        """
        # Get the child
        child = Child.get_by_id(child_id)
        if not child:
            return False, "Child not found"
        
        # Check if user belongs to the same family as the child
        user = User.get_by_id(user_id)
        if not user:
            return False, "User not found"
        
        if user.family_id != child.family_id:
            return False, "You can only remove children from your own family"
        
        try:
            child_name = child.name
            child.delete()
            return True, None
        except Exception as e:
            return False, f"Failed to remove child: {str(e)}"
    
    @staticmethod
    def get_family_children(user_id):
        """Get all children in the user's family.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            list: List of Child objects
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return []
        
        return Child.get_by_family(user.family_id)
