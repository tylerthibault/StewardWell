"""
Chore Logic

Contains business logic for chore management and completion.
"""

from datetime import datetime
from src.models.chore_model import Chore
from src.models.family_points_model import FamilyPoints, PointsTransaction
from src.models.child_model import Child
from src.models.user_model import User


class ChoreLogic:
    """Business logic for chore operations."""
    
    @staticmethod
    def create_chore(family_id, name, description, points_reward, assigned_to_type, 
                    created_by, assigned_to_id=None, due_date=None):
        """Create a new chore.
        
        Args:
            family_id (int): ID of the family
            name (str): Name of the chore
            description (str): Description
            points_reward (int): Points earned when completed
            assigned_to_type (str): 'child', 'adult', or 'any'
            created_by (int): ID of the user creating the chore
            assigned_to_id (int, optional): Specific child or user ID if assigned
            due_date (datetime, optional): Due date for the chore
            
        Returns:
            tuple: (success: bool, chore: Chore|None, error: str|None)
        """
        try:
            if not name or len(name.strip()) < 1:
                return False, None, "Chore name is required"
            
            if points_reward < 0:
                return False, None, "Points reward cannot be negative"
            
            if assigned_to_type not in ['child', 'adult', 'any']:
                return False, None, "Invalid assignment type"
            
            # Validate assigned_to_id if specific assignment
            if assigned_to_id is not None:
                if assigned_to_type == 'child':
                    child = Child.get_by_id(assigned_to_id)
                    if not child or child.family_id != family_id:
                        return False, None, "Invalid child assignment"
                elif assigned_to_type == 'adult':
                    user = User.get_by_id(assigned_to_id)
                    if not user or user.family_id != family_id:
                        return False, None, "Invalid adult assignment"
            
            chore = Chore.create_chore(
                family_id=family_id,
                name=name.strip(),
                description=description.strip() if description else "",
                points_reward=points_reward,
                assigned_to_type=assigned_to_type,
                created_by=created_by,
                assigned_to_id=assigned_to_id,
                due_date=due_date
            )
            return True, chore, None
        except Exception as e:
            return False, None, f"Failed to create chore: {str(e)}"
    
    @staticmethod
    def complete_chore(chore_id, completed_by_type, completed_by_id):
        """Complete a chore and award family points.
        
        Args:
            chore_id (int): ID of the chore to complete
            completed_by_type (str): 'child' or 'adult'
            completed_by_id (int): ID of the child or user completing the chore
            
        Returns:
            tuple: (success: bool, points_earned: int, message: str)
        """
        try:
            chore = Chore.get_by_id(chore_id)
            if not chore:
                return False, 0, "Chore not found"
            
            if chore.status != 'pending':
                return False, 0, "Chore is not pending"
            
            # Validate completer
            if completed_by_type == 'child':
                child = Child.get_by_id(completed_by_id)
                if not child or child.family_id != chore.family_id:
                    return False, 0, "Invalid child"
                completer_name = child.name
            elif completed_by_type == 'adult':
                user = User.get_by_id(completed_by_id)
                if not user or user.family_id != chore.family_id:
                    return False, 0, "Invalid adult"
                completer_name = user.username
            else:
                return False, 0, "Invalid completer type"
            
            # Check if assignment allows this completer
            if chore.assigned_to_type == 'child' and completed_by_type != 'child':
                return False, 0, "This chore can only be completed by children"
            elif chore.assigned_to_type == 'adult' and completed_by_type != 'adult':
                return False, 0, "This chore can only be completed by adults"
            elif chore.assigned_to_id is not None and chore.assigned_to_id != completed_by_id:
                return False, 0, "This chore is assigned to someone else"
            
            # Mark chore as completed
            chore.complete_chore(completed_by_type, completed_by_id)
            
            # Award points to family pool
            if chore.points_reward > 0:
                family_points = FamilyPoints.get_by_family(chore.family_id)
                family_points.add_points(chore.points_reward)
                
                # Record transaction
                user_id = completed_by_id if completed_by_type == 'adult' else None
                child_id = completed_by_id if completed_by_type == 'child' else None
                
                PointsTransaction.create_transaction(
                    family_id=chore.family_id,
                    user_id=user_id,
                    child_id=child_id,
                    amount=chore.points_reward,
                    transaction_type='chore_completion',
                    description=f"{completer_name} completed: {chore.name}",
                    reference_id=chore.id
                )
                
                message = f"{completer_name} completed '{chore.name}' and earned {chore.points_reward} family points!"
            else:
                message = f"{completer_name} completed '{chore.name}'"
            
            return True, chore.points_reward, message
        except Exception as e:
            return False, 0, f"Failed to complete chore: {str(e)}"
    
    @staticmethod
    def get_available_chores_for_child(family_id, child_id):
        """Get chores available for a specific child.
        
        Args:
            family_id (int): ID of the family
            child_id (int): ID of the child
            
        Returns:
            list: List of chores the child can complete
        """
        try:
            # Get chores assigned to this child
            assigned_chores = Chore.get_assigned_to_child(family_id, child_id)
            
            # Get chores available for anyone
            any_chores = Chore.get_available_for_anyone(family_id)
            
            return assigned_chores + any_chores
        except Exception as e:
            return []
    
    @staticmethod
    def get_available_chores_for_adult(family_id, user_id):
        """Get chores available for a specific adult.
        
        Args:
            family_id (int): ID of the family
            user_id (int): ID of the adult
            
        Returns:
            list: List of chores the adult can complete
        """
        try:
            # Get chores assigned to this adult
            assigned_chores = Chore.get_assigned_to_adult(family_id, user_id)
            
            # Get chores available for anyone
            any_chores = Chore.get_available_for_anyone(family_id)
            
            return assigned_chores + any_chores
        except Exception as e:
            return []
    
    @staticmethod
    def get_family_chores_summary(family_id):
        """Get summary of all family chores.
        
        Args:
            family_id (int): ID of the family
            
        Returns:
            dict: Chores organized by status and assignment
        """
        try:
            pending_chores = Chore.get_by_family(family_id, status='pending')
            completed_chores = Chore.get_by_family(family_id, status='completed')
            
            return {
                'pending': pending_chores,
                'completed': completed_chores[:20],  # Last 20 completed
                'total_pending': len(pending_chores),
                'total_completed': len(Chore.get_by_family(family_id, status='completed'))
            }
        except Exception as e:
            return {
                'pending': [],
                'completed': [],
                'total_pending': 0,
                'total_completed': 0,
                'error': str(e)
            }
    
    @staticmethod
    def delete_chore(chore_id, user_id):
        """Delete a chore (only by creator or family manager).
        
        Args:
            chore_id (int): ID of the chore to delete
            user_id (int): ID of the user requesting deletion
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            chore = Chore.get_by_id(chore_id)
            if not chore:
                return False, "Chore not found"
            
            # Check if user can delete (creator or family manager)
            user = User.get_by_id(user_id)
            if not user:
                return False, "Invalid user"
            
            from src.models.family_model import Family
            family = Family.get_by_id(chore.family_id)
            
            can_delete = (chore.created_by == user_id or 
                         (family and family.creator_id == user_id))
            
            if not can_delete:
                return False, "Only the chore creator or family manager can delete chores"
            
            if chore.status == 'completed':
                return False, "Cannot delete completed chores"
            
            # Archive instead of delete to preserve data integrity
            chore.archive_chore()
            return True, f"Chore '{chore.name}' has been archived"
        except Exception as e:
            return False, f"Failed to delete chore: {str(e)}"