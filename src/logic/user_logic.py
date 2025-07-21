"""
User Logic

Contains all business logic related to user management.
Following the fat logic principle - handles business rules and validation.
"""

from src.models.user_model import User


class UserLogic:
    """Business logic for user operations."""
    
    @staticmethod
    def update_user_profile(user_id, username=None, email=None):
        """Update a user's profile information.
        
        Args:
            user_id (int): ID of the user to update
            username (str, optional): New username
            email (str, optional): New email
            
        Returns:
            tuple: (success: bool, user: User|None, error: str|None)
        """
        # Get the user
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        # Validate username if provided
        if username is not None:
            username = username.strip()
            if len(username) < 3:
                return False, None, "Username must be at least 3 characters long"
            
            # Check if username is already taken by another user
            if username != user.username and User.username_exists(username):
                return False, None, "Username is already taken"
        
        # Validate email if provided
        if email is not None:
            email = email.strip().lower()
            if not email or '@' not in email:
                return False, None, "Please provide a valid email address"
            
            # Check if email is already taken by another user
            if email != user.email and User.email_exists(email):
                return False, None, "Email is already taken"
        
        try:
            # Update the user
            user.update_profile(username=username, email=email)
            return True, user, None
        except Exception as e:
            return False, None, f"Failed to update profile: {str(e)}"
    
    @staticmethod
    def get_family_members(user_id):
        """Get all family members for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            list: List of User objects (family members)
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return []
        
        from src.models.family_model import Family
        family = Family.get_by_id(user.family_id)
        if not family:
            return []
        
        return family.users