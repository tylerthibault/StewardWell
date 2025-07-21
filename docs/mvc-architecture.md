# StewardWell MVC Architecture

## Overview
The StewardWell application has been successfully reorganized into a proper Model-View-Controller (MVC) architecture following Flask best practices.

## Project Structure

```
StewardWell/
├── config.py                 # Application configuration
├── server.py                 # Development server entry point
├── run.py                    # Production server entry point
├── requirements.txt          # Python dependencies
├── src/                      # Main application package
│   ├── __init__.py           # Application factory
│   ├── controllers/          # Controllers (thin - handle requests/responses)
│   │   ├── main.py           # Main routes (landing, dashboard)
│   │   ├── auth_controller.py # Authentication routes
│   │   ├── family_controller.py # Family management routes
│   │   └── child_controller.py  # Child management routes
│   ├── models/               # Models (thin - database operations only)
│   │   ├── main.py           # Model imports
│   │   ├── user_model.py     # User database model
│   │   ├── family_model.py   # Family database model
│   │   └── child_model.py    # Child database model
│   ├── logic/                # Business Logic (fat - business rules)
│   │   ├── auth_logic.py     # Authentication business logic
│   │   ├── family_logic.py   # Family business logic
│   │   └── child_logic.py    # Child business logic
│   ├── utils/                # Utility functions
│   │   └── helpers.py        # Common helper functions
│   ├── templates/            # HTML templates
│   └── static/               # Static files (CSS, JS, images)
├── instance/
│   └── stewardwell.db        # SQLite database
└── docs/
    └── deploy.md             # Deployment documentation
```

## Architecture Principles

### 1. Application Factory Pattern
- `src/__init__.py` contains the `create_app()` factory function
- Enables better testing and configuration management
- Cleanly separates application creation from running

### 2. Thin Controllers (Request/Response Handling)
Controllers in `src/controllers/` are minimal and only handle:
- Request parsing and validation
- Calling appropriate business logic functions
- Returning responses and handling redirects
- Flash message management

### 3. Fat Logic Layer (Business Rules)
Logic modules in `src/logic/` contain all business rules:
- Input validation and sanitization
- Business rule enforcement
- Complex operations and workflows
- Data processing and transformation

### 4. Thin Models (Database Operations)
Models in `src/models/` focus solely on database interactions:
- CRUD operations
- Database schema definitions
- Query building
- Simple data validation

### 5. Blueprint-Based Routing
- Each functional area has its own blueprint
- Clean separation of concerns
- Better organization and maintainability

## Key Components

### Models
- **User**: Parent/guardian accounts with authentication
- **Family**: Family groups with unique codes
- **Child**: Child profiles within families

### Controllers
- **Main**: Landing page and dashboard routes
- **Auth**: Registration, login, logout
- **Family**: Family creation and joining
- **Child**: Adding and removing children

### Logic Layers
- **AuthLogic**: User registration and authentication validation
- **FamilyLogic**: Family creation, joining, and management rules
- **ChildLogic**: Child management with family validation

## Benefits of This Structure

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Testability**: Business logic is isolated and easily testable
3. **Maintainability**: Changes are localized to appropriate layers
4. **Scalability**: Easy to add new features following the same pattern
5. **Code Reusability**: Logic can be reused across different controllers
6. **Security**: Input validation and business rules are centralized

## Running the Application

### Development Mode
```bash
python server.py
```

### Production Mode
```bash
python run.py
```

Both entry points now use the application factory pattern and properly initialize the MVC structure.

## Future Enhancements

The new MVC structure makes it easy to add:
- API endpoints (new controllers)
- Additional business logic (new logic modules)
- More complex data models (new model files)
- Background tasks and services
- Comprehensive testing suites

## Migration Notes

- All existing functionality has been preserved
- Database schema remains unchanged
- Templates and static files are unchanged
- Configuration system is maintained
- Flask-Login integration is preserved

The application maintains full backward compatibility while providing a much cleaner, more maintainable codebase.
