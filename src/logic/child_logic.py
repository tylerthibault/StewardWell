"""
Child Logic

Contains all business logic related to child management.
Following the fat logic principle - handles business rules and validation.
"""

from datetime import date, datetime
from src.models.child_model import Child
from src.models.user_model import User


class ChildLogic:
    """Business logic for child operations."""
    
    @staticmethod
    def add_child(name, user_id, age=None, birthdate=None, pin=None):
        """Add a new child to the user's family.
        
        Args:
            name (str): Name of the child
            user_id (int): ID of the user adding the child
            age (int, optional): Age of the child (for backward compatibility)
            birthdate (str or date, optional): Birthdate of the child
            pin (str, optional): PIN for the child
            
        Returns:
            tuple: (success: bool, child: Child|None, error: str|None)
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return False, None, "Child name must be at least 2 characters long"
        
        name = name.strip()
        
        # Validate and convert birthdate if provided
        parsed_birthdate = None
        if birthdate:
            try:
                if isinstance(birthdate, str):
                    parsed_birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()
                else:
                    parsed_birthdate = birthdate
                    
                # Validate birthdate is not in the future and reasonable
                if parsed_birthdate > date.today():
                    return False, None, "Birthdate cannot be in the future"
                if parsed_birthdate.year < date.today().year - 18:
                    return False, None, "Child cannot be older than 18 years"
            except ValueError:
                return False, None, "Invalid birthdate format. Use YYYY-MM-DD"
        
        # Validate age if provided (for backward compatibility)
        if age is not None:
            try:
                age = int(age)
                if age < 0 or age > 18:
                    return False, None, "Age must be between 0 and 18"
            except (ValueError, TypeError):
                return False, None, "Age must be a valid number"
        
        # Validate PIN if provided
        if pin is not None:
            pin = pin.strip()
            if pin and not pin.isdigit():
                return False, None, "PIN must contain only numbers"
            if pin and (len(pin) < 4 or len(pin) > 10):
                return False, None, "PIN must be between 4 and 10 digits"
        
        # Check if user belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if not user.family_id:
            return False, None, "You must be part of a family to add children"
        
        try:
            # Create the child
            child = Child.create_child(name, user.family_id, user_id, age, parsed_birthdate, pin)
            return True, child, None
        except Exception as e:
            return False, None, f"Failed to add child: {str(e)}"
    
    @staticmethod
    def update_child(child_id, user_id, name=None, birthdate=None, pin=None, age=None):
        """Update a child's information.
        
        Args:
            child_id (int): ID of the child to update
            user_id (int): ID of the user making the update
            name (str, optional): New name
            birthdate (str or date, optional): New birthdate
            pin (str, optional): New PIN
            age (int, optional): New age (for backward compatibility)
            
        Returns:
            tuple: (success: bool, child: Child|None, error: str|None)
        """
        # Get the child
        child = Child.get_by_id(child_id)
        if not child:
            return False, None, "Child not found"
        
        # Check if user belongs to the same family as the child
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id != child.family_id:
            return False, None, "You can only update children from your own family"
        
        # Validate name if provided
        if name is not None:
            name = name.strip()
            if len(name) < 2:
                return False, None, "Child name must be at least 2 characters long"
        
        # Validate and convert birthdate if provided
        parsed_birthdate = None
        if birthdate is not None:
            if birthdate:  # Only validate if not empty string
                try:
                    if isinstance(birthdate, str):
                        parsed_birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()
                    else:
                        parsed_birthdate = birthdate
                        
                    # Validate birthdate is not in the future and reasonable
                    if parsed_birthdate > date.today():
                        return False, None, "Birthdate cannot be in the future"
                    if parsed_birthdate.year < date.today().year - 18:
                        return False, None, "Child cannot be older than 18 years"
                except ValueError:
                    return False, None, "Invalid birthdate format. Use YYYY-MM-DD"
            else:
                parsed_birthdate = None  # Empty string means clear birthdate
        
        # Validate age if provided (for backward compatibility)
        if age is not None:
            if age:  # Only validate if not empty
                try:
                    age = int(age)
                    if age < 0 or age > 18:
                        return False, None, "Age must be between 0 and 18"
                except (ValueError, TypeError):
                    return False, None, "Age must be a valid number"
            else:
                age = None  # Empty string means clear age
        
        # Validate PIN if provided
        validated_pin = pin
        if pin is not None:
            if pin:  # Only validate if not empty string
                validated_pin = pin.strip()
                if not validated_pin.isdigit():
                    return False, None, "PIN must contain only numbers"
                if len(validated_pin) < 4 or len(validated_pin) > 10:
                    return False, None, "PIN must be between 4 and 10 digits"
            else:
                validated_pin = None  # Empty string means clear PIN
        
        try:
            # Update the child
            child.update(name=name, birthdate=parsed_birthdate, pin=validated_pin, age=age)
            return True, child, None
        except Exception as e:
            return False, None, f"Failed to update child: {str(e)}"
    
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
