---
applyTo: 'python'
---
# StewardWell Python Coding Guidelines

## Overview
Follow these coding standards when working with Python code in the StewardWell project. Prioritize code clarity and maintainability over brevity. Write clean, functional code that is easy to understand and debug.

## Architecture Principles

### Controller Layer - Thin Controllers
Controllers should be minimal and only handle:
- Request/response management
- Input validation and sanitization
- Calling appropriate business logic functions
- Error handling and HTTP status codes
- Authentication/authorization checks

```python
def create_family(request):
    """Handle family creation request."""
    try:
        # Validate input
        family_data = validate_family_data(request.json)
        
        # Call business logic
        family = family_logic.create_new_family(family_data, request.user.id)
        
        # Return response
        return jsonify({
            'success': True,
            'family': family.to_dict(),
            'family_code': family.code
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Family creation failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

### Logic Layer - Fat Logic Files
Business logic files should contain all business rules and complex operations:
- Data processing and transformation
- Business rule validation
- Complex calculations
- Workflow orchestration
- Integration between different models

```python
def create_new_family(family_data: dict, creator_id: int) -> Family:
    """Create a new family with the creator as family manager.
    
    Args:
        family_data: Dictionary containing family information
        creator_id: ID of the user creating the family
        
    Returns:
        Family: The newly created family object
        
    Raises:
        BusinessLogicError: If family creation rules are violated
    """
    # Generate unique family code
    family_code = generate_unique_family_code()
    
    # Create family record
    family = family_model.create_family(
        name=family_data['name'],
        code=family_code
    )
    
    # Add creator as family manager
    family_member_model.add_family_member(
        family_id=family.id,
        user_id=creator_id,
        role='manager'
    )
    
    # Initialize default family settings
    initialize_family_defaults(family.id)
    
    return family
```

### Model Layer - Thin Database Models
Models should focus solely on database interactions:
- CRUD operations
- Database schema definitions
- Query building
- Data validation at the database level

```python
def create_family(name: str, code: str) -> Family:
    """Create a new family record in the database.
    
    Args:
        name: The family name
        code: Unique family code
        
    Returns:
        Family: The created family object
        
    Raises:
        DatabaseError: If database operation fails
    """
    family = Family(name=name, code=code)
    db.session.add(family)
    db.session.commit()
    return family
```

## Code Style Guidelines

### Function Design
- **Single Responsibility**: Each function should do ONE thing well
- **Maximum of 2 operations**: If a function must do multiple things, limit to 2 related operations
- **Functional approach**: Input → Processing → Output (no side effects when possible)
- **Linear flow**: Code should read top to bottom without complex branching

### Documentation Requirements
All functions must have clear docstrings following Google style:

```python
def process_chore_completion(chore_id: int, child_id: int, completion_data: dict) -> ChoreCompletion:
    """Process and record a child's chore completion.
    
    Validates the completion data, updates the chore status, and calculates
    any rewards or points earned by the child.
    
    Args:
        chore_id: The ID of the completed chore
        child_id: The ID of the child completing the chore
        completion_data: Dictionary containing completion details and evidence
        
    Returns:
        ChoreCompletion: The recorded completion with calculated rewards
        
    Raises:
        ValidationError: If completion data is invalid
        PermissionError: If child is not assigned to this chore
        BusinessLogicError: If chore cannot be completed in current state
    """
    pass
```

### Variable and Function Naming
- Use descriptive, clear names over short ones
- Prefer `calculate_monthly_allowance()` over `calc_allowance()`
- Use verb_noun pattern for functions: `validate_user_input()`, `generate_family_code()`
- Use descriptive variable names: `family_member_count` not `count`

### Error Handling
- Use specific exception types
- Always include meaningful error messages
- Log errors with context
- Handle errors at the appropriate layer

```python
class FamilyBusinessLogicError(Exception):
    """Raised when family business rules are violated."""
    pass

def add_child_to_family(family_id: int, child_data: dict) -> Child:
    """Add a new child to a family.
    
    Args:
        family_id: The ID of the family
        child_data: Dictionary containing child information
        
    Returns:
        Child: The created child object
        
    Raises:
        FamilyBusinessLogicError: If family rules prevent adding child
    """
    # Validate family exists and is active
    family = family_model.get_family_by_id(family_id)
    if not family:
        raise FamilyBusinessLogicError(f"Family {family_id} not found")
    
    # Check family size limits
    current_child_count = child_model.count_children_in_family(family_id)
    if current_child_count >= MAX_CHILDREN_PER_FAMILY:
        raise FamilyBusinessLogicError("Family has reached maximum child limit")
    
    # Create child
    return child_model.create_child(family_id, child_data)
```

## File Organization

### Directory Structure
```
src/
├── controllers/           # Thin controllers (HTTP handling)
├── logic/                # Fat business logic files
├── models/               # Thin database models
├── utils/                # Helper functions and utilities
├── validators/           # Input validation functions
└── exceptions/           # Custom exception classes
```

### Import Organization
```python
# Standard library imports
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Third-party imports
from flask import request, jsonify
from sqlalchemy import and_, or_

# Local application imports
from src.models.family import Family
from src.logic.family_logic import create_new_family
from src.validators.family_validators import validate_family_data
from src.exceptions.family_exceptions import FamilyBusinessLogicError
```

## Testing Guidelines

### Test Structure
- Test files mirror source structure: `test_family_logic.py` for `family_logic.py`
- Use descriptive test names: `test_create_family_with_valid_data_returns_family_object()`
- Test one scenario per test function
- Include docstrings for complex test scenarios

### Test Categories
1. **Unit tests**: Test individual functions in isolation
2. **Integration tests**: Test logic layer with database
3. **Controller tests**: Test HTTP endpoints with mocked logic

## Code Quality Tools

### Required Tools
- **Black**: Code formatting (line length: 100 characters)
- **isort**: Import sorting
- **flake8**: Linting with these rules:
  - Max line length: 100
  - Max complexity: 10
  - Docstring requirements enabled
- **mypy**: Type checking (gradual adoption)

### Pre-commit Hooks
All code must pass these checks before commit:
```bash
black --check --line-length 100 .
isort --check-only .
flake8 --max-line-length 100 --max-complexity 10 .
mypy src/ --ignore-missing-imports
```

## Performance Guidelines

### Database Queries
- Use explicit queries rather than ORM magic
- Implement pagination for list endpoints
- Use database indexes appropriately
- Avoid N+1 query problems

### Caching Strategy
- Cache expensive calculations in logic layer
- Use Redis for session data and temporary state
- Implement cache invalidation strategies

## Security Guidelines

### Input Validation
- Validate all user input at controller layer
- Sanitize data before database operations
- Use parameterized queries to prevent SQL injection

### Authentication & Authorization
- Check permissions at controller layer
- Use role-based access control
- Implement family-scoped data access

## Module Integration

### Module Interface
Each module should provide a clean interface:
```python
class ChoreModule:
    """Interface for the chore management module."""
    
    def register_routes(self, app):
        """Register module routes with the Flask app."""
        pass
    
    def get_dashboard_summary(self, family_id: int) -> dict:
        """Get chore summary for family dashboard."""
        pass
```

### Configuration
- Use environment variables for configuration
- Provide sensible defaults
- Document all configuration options

## Examples of Good vs Bad Code

### Good - Thin Controller
```python
def update_child_profile(child_id):
    """Update a child's profile information."""
    try:
        child_data = validate_child_update_data(request.json)
        updated_child = child_logic.update_child_profile(child_id, child_data)
        return jsonify(updated_child.to_dict()), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
```

### Bad - Fat Controller
```python
def update_child_profile(child_id):
    """Update a child's profile information."""
    # Don't do database operations directly in controller
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404
    
    # Don't do business logic in controller
    if request.json.get('age') and request.json['age'] < 3:
        return jsonify({'error': 'Child too young'}), 400
    
    # Multiple database operations in controller is wrong
    child.name = request.json.get('name', child.name)
    child.age = request.json.get('age', child.age)
    db.session.commit()
    
    return jsonify(child.to_dict()), 200
```

Remember: **Clarity over cleverness**. Write code that your future self and teammates can easily understand and maintain.