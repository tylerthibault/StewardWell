"""
Authentication Logic

Contains all business logic related to user authentication and registration.
Following the fat logic principle - handles business rules and validation.
"""

from src.models.user_model import User


class AuthLogic:
    """Business logic for authentication operations."""
    
    @staticmethod
    def register_user(username, email, password):
        """Register a new user with validation.
        
        Args:
            username (str): Desired username
            email (str): User's email address
            password (str): Plain text password
            
        Returns:
            tuple: (success: bool, user: User|None, error: str|None)
        """
        # Validate input
        if not username or len(username.strip()) < 3:
            return False, None, "Username must be at least 3 characters long"
        
        if not email or '@' not in email:
            return False, None, "Please provide a valid email address"
        
        if not password or len(password) < 6:
            return False, None, "Password must be at least 6 characters long"
        
        username = username.strip()
        email = email.strip().lower()
        
        # Check if user already exists
        if User.username_exists(username):
            return False, None, "Username already exists"
        
        if User.email_exists(email):
            return False, None, "Email already exists"
        
        # Create new user
        try:
            user = User.create_user(username, email, password)
            return True, user, None
        except Exception as e:
            return False, None, f"Failed to create user: {str(e)}"
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user login attempt.
        
        Args:
            username (str): Username or email
            password (str): Plain text password
            
        Returns:
            tuple: (success: bool, user: User|None, error: str|None)
        """
        if not username or not password:
            return False, None, "Username and password are required"
        
        username = username.strip()
        
        # Try to find user by username first, then by email
        user = User.get_by_username(username)
        if not user:
            user = User.get_by_email(username.lower())
        
        if not user:
            return False, None, "Invalid username or password"
        
        if not user.check_password(password):
            return False, None, "Invalid username or password"
        
        return True, user, None
