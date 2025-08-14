"""
Chore Logic

Contains all business logic related to chore management.
Following the fat logic principle - handles business rules and validation.
"""

from datetime import datetime, timedelta
from src.models.chore_model import Chore
from src.models.child_model import Child
from src.models.user_model import User


class ChoreLogic:
    """Business logic for chore operations."""
    
    @staticmethod
    def create_chore(name, user_id, description=None, coin_amount=0, point_amount=0, 
                     is_recurring=False, recurring_days=None, assigned_child_id=None, 
                     due_date=None, notes=None, priority='medium'):
        """Create a new chore with validation.
        
        Args:
            name (str): Name of the chore
            user_id (int): ID of the user creating the chore
            description (str, optional): Description of the chore
            coin_amount (int, optional): Individual reward amount
            point_amount (int, optional): Family reward amount
            is_recurring (bool, optional): Whether chore recurs
            recurring_days (list, optional): List of day numbers for recurring
            assigned_child_id (int, optional): ID of assigned child
            due_date (datetime, optional): Due date for the chore
            notes (str, optional): Additional notes
            priority (str, optional): Priority level
            
        Returns:
            tuple: (success: bool, chore: Chore|None, error: str|None)
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return False, None, "Chore name must be at least 2 characters long"
        
        name = name.strip()
        
        # Validate priority
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        # Validate coin and point amounts
        try:
            coin_amount = max(0, int(coin_amount or 0))
            point_amount = max(0, int(point_amount or 0))
        except (ValueError, TypeError):
            return False, None, "Coin and point amounts must be valid numbers"
        
        # Check if user belongs to a family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if not user.family_id:
            return False, None, "You must be part of a family to create chores"
        
        # Validate assigned child belongs to same family
        if assigned_child_id:
            child = Child.get_by_id(assigned_child_id)
            if not child or child.family_id != user.family_id:
                return False, None, "Assigned child must be from your family"
        
        # Validate recurring days if recurring
        if is_recurring and recurring_days:
            if not isinstance(recurring_days, list) or not all(isinstance(day, int) and 0 <= day <= 6 for day in recurring_days):
                return False, None, "Recurring days must be a list of integers from 0 (Monday) to 6 (Sunday)"
        
        try:
            # Create the chore
            chore = Chore.create_chore(
                name=name,
                family_id=user.family_id,
                created_by=user_id,
                description=description,
                coin_amount=coin_amount,
                point_amount=point_amount,
                is_recurring=is_recurring,
                recurring_days=recurring_days,
                assigned_child_id=assigned_child_id,
                due_date=due_date,
                notes=notes,
                priority=priority
            )
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to create chore: {str(e)}"
    
    @staticmethod
    def update_chore(chore_id, user_id, **kwargs):
        """Update a chore with validation.
        
        Args:
            chore_id (int): ID of the chore to update
            user_id (int): ID of the user requesting update
            **kwargs: Fields to update
            
        Returns:
            tuple: (success: bool, chore: Chore|None, error: str|None)
        """
        # Get the chore
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, None, "Chore not found"
        
        # Check if user belongs to the same family as the chore
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id != chore.family_id:
            return False, None, "You can only update chores from your own family"
        
        # Validate name if provided
        if 'name' in kwargs:
            name = kwargs['name']
            if not name or len(name.strip()) < 2:
                return False, None, "Chore name must be at least 2 characters long"
            kwargs['name'] = name.strip()
        
        # Validate priority if provided
        if 'priority' in kwargs and kwargs['priority'] not in ['low', 'medium', 'high']:
            kwargs['priority'] = 'medium'
        
        # Validate coin and point amounts if provided
        for field in ['coin_amount', 'point_amount']:
            if field in kwargs:
                try:
                    kwargs[field] = max(0, int(kwargs[field] or 0))
                except (ValueError, TypeError):
                    return False, None, f"{field.replace('_', ' ').title()} must be a valid number"
        
        # Validate assigned child belongs to same family
        if 'assigned_child_id' in kwargs and kwargs['assigned_child_id']:
            child = Child.get_by_id(kwargs['assigned_child_id'])
            if not child or child.family_id != user.family_id:
                return False, None, "Assigned child must be from your family"
        
        # Validate recurring days if provided
        if 'recurring_days' in kwargs and kwargs['recurring_days']:
            recurring_days = kwargs['recurring_days']
            if not isinstance(recurring_days, list) or not all(isinstance(day, int) and 0 <= day <= 6 for day in recurring_days):
                return False, None, "Recurring days must be a list of integers from 0 (Monday) to 6 (Sunday)"
        
        try:
            chore.update_chore(**kwargs)
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to update chore: {str(e)}"
    
    @staticmethod
    def delete_chore(chore_id, user_id):
        """Delete a chore with validation.
        
        Args:
            chore_id (int): ID of the chore to delete
            user_id (int): ID of the user requesting deletion
            
        Returns:
            tuple: (success: bool, error: str|None)
        """
        # Get the chore
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, "Chore not found"
        
        # Check if user belongs to the same family as the chore
        user = User.get_by_id(user_id)
        if not user:
            return False, "User not found"
        
        if user.family_id != chore.family_id:
            return False, "You can only delete chores from your own family"
        
        try:
            chore_name = chore.name
            chore.delete()
            return True, None
        except Exception as e:
            return False, f"Failed to delete chore: {str(e)}"
    
    @staticmethod
    def assign_chore(chore_id, child_id, user_id):
        """Assign a chore to a child with validation.
        
        Args:
            chore_id (int): ID of the chore to assign
            child_id (int): ID of the child to assign to
            user_id (int): ID of the user making the assignment
            
        Returns:
            tuple: (success: bool, chore: Chore|None, error: str|None)
        """
        # Get the chore
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, None, "Chore not found"
        
        # Get the child
        child = Child.get_by_id(child_id)
        if not child:
            return False, None, "Child not found"
        
        # Check if user belongs to the same family
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id != chore.family_id or user.family_id != child.family_id:
            return False, None, "You can only assign chores within your own family"
        
        try:
            chore.assign_to_child(child_id)
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to assign chore: {str(e)}"
    
    @staticmethod
    def complete_chore(chore_id, user_id):
        """Mark a chore as completed with validation.
        
        Args:
            chore_id (int): ID of the chore to complete
            user_id (int): ID of the user completing the chore
            
        Returns:
            tuple: (success: bool, chore: Chore|None, error: str|None)
        """
        # Get the chore
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, None, "Chore not found"
        
        # Check if user belongs to the same family as the chore
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        
        if user.family_id != chore.family_id:
            return False, None, "You can only complete chores from your own family"
        
        # Check if chore is already completed
        if chore.status == 'completed':
            return False, None, "Chore is already completed"
        
        try:
            chore.complete()
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to complete chore: {str(e)}"

    @staticmethod
    def submit_chore(chore_id, child_id, user_id):
        """Child submits a chore for approval. Sets status to 'submitted'.

        Args:
            chore_id (int): ID of the chore to submit
            child_id (int): ID of the child submitting
            user_id (int): ID of the current user (parent in kids view)

        Returns:
            tuple: (success: bool, chore: Chore|None, error: str|None)
        """
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, None, "Chore not found"

        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return False, None, "User not found"

        child = Child.get_by_id(child_id)
        if not child:
            return False, None, "Child not found"

        if user.family_id != chore.family_id or child.family_id != chore.family_id:
            return False, None, "Unauthorized for this family"

        if chore.assigned_child_id != child.id:
            return False, None, "This chore isn't assigned to this child"

        if chore.status == 'completed':
            return False, None, "Chore is already completed"

        try:
            chore.status = 'submitted'
            chore.save()
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to submit chore: {str(e)}"

    @staticmethod
    def approve_chore(chore_id, user_id):
        """Adult approves a submitted chore; marks as completed and awards rewards later.

        Returns tuple(success, chore, error).
        """
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, None, "Chore not found"
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        if user.family_id != chore.family_id:
            return False, None, "Unauthorized for this family"
        if chore.status not in ['submitted', 'pending']:
            return False, None, "Chore is not awaiting approval"
        try:
            chore.complete()
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to approve chore: {str(e)}"

    @staticmethod
    def reject_chore(chore_id, user_id):
        """Adult rejects a submitted chore; returns to pending for rework.

        Returns tuple(success, chore, error).
        """
        chore = Chore.get_by_id(chore_id)
        if not chore:
            return False, None, "Chore not found"
        user = User.get_by_id(user_id)
        if not user:
            return False, None, "User not found"
        if user.family_id != chore.family_id:
            return False, None, "Unauthorized for this family"
        if chore.status != 'submitted':
            return False, None, "Only submitted chores can be rejected"
        try:
            chore.status = 'pending'
            chore.save()
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to reject chore: {str(e)}"
    
    @staticmethod
    def get_family_chores(user_id, status=None, child_id=None):
        """Get all chores for a user's family with optional filtering.
        
        Args:
            user_id (int): ID of the user
            status (str, optional): Filter by status
            child_id (int, optional): Filter by assigned child
            
        Returns:
            list: List of Chore objects
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return []
        
        chores = Chore.get_by_family(user.family_id)
        
        # Apply filters
        if status:
            chores = [chore for chore in chores if chore.status == status]
        
        if child_id:
            chores = [chore for chore in chores if chore.assigned_child_id == child_id]
        
        return chores
    
    @staticmethod
    def get_available_chores(user_id):
        """Get available chores for a user's family.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            list: List of available Chore objects
        """
        user = User.get_by_id(user_id)
        if not user or not user.family_id:
            return []
        
        return Chore.get_available_for_family(user.family_id)
    
    @staticmethod
    def get_child_chores(user_id, child_id):
        """Get chores assigned to a specific child with family validation.
        
        Args:
            user_id (int): ID of the user
            child_id (int): ID of the child
            
        Returns:
            list: List of Chore objects assigned to the child
        """
        # Verify user and child belong to same family
        user = User.get_by_id(user_id)
        child = Child.get_by_id(child_id)
        
        if not user or not child or user.family_id != child.family_id:
            return []
        
        return Chore.get_by_child(child_id)