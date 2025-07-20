# StewardWell Database Schema

**Author:** tylerthibault  
**Last Updated:** 2025-07-20 15:45:16 UTC

## Core Tables - Parent Application

### Users
Stores information about parent users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| first_name | VARCHAR(50) | NOT NULL | User's first name |
| last_name | VARCHAR(50) | NOT NULL | User's last name |
| email | VARCHAR(120) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(128) | NOT NULL | Hashed password |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### Families
Stores family units.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Family name |
| family_code | VARCHAR(8) | UNIQUE, NOT NULL | Unique code for family identification |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### FamilyMembers
Junction table connecting users (parents) to families. Also handles family invitations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to Users table |
| family_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to Families table |
| role | VARCHAR(20) | DEFAULT 'member' | Role in family ('manager', 'member') |
| status | VARCHAR(20) | DEFAULT 'pending' | Status ('pending', 'active', 'inactive') |
| invited_by | INTEGER | FOREIGN KEY, NULL | Reference to Users table (who sent invitation) |
| invitation_email | VARCHAR(120) | NULL | Email used for invitation (if user not registered yet) |
| invitation_token | VARCHAR(64) | UNIQUE, NULL | Token for email invitations |
| invitation_expires | DATETIME | NULL | When invitation expires |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Created timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Updated timestamp |
| UNIQUE | (user_id, family_id) | | Prevents duplicate memberships |

### Children
Stores information about child users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| first_name | VARCHAR(50) | NOT NULL | Child's first name |
| last_name | VARCHAR(50) | NOT NULL | Child's last name |
| family_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to Families table |
| pin | VARCHAR(10) | NOT NULL | PIN for child login (hashed) |
| birth_date | DATE | NULL | Child's birth date |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### Messages
Stores messages between family members.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| family_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to Families table |
| sender_user_id | INTEGER | FOREIGN KEY, NULL | Reference to Users table (if sent by parent) |
| sender_child_id | INTEGER | FOREIGN KEY, NULL | Reference to Children table (if sent by child) |
| recipient_user_id | INTEGER | FOREIGN KEY, NULL | Reference to Users table (if for parent) |
| recipient_child_id | INTEGER | FOREIGN KEY, NULL | Reference to Children table (if for child) |
| is_family_message | BOOLEAN | DEFAULT FALSE | If true, message is to all family members |
| subject | VARCHAR(100) | NULL | Message subject |
| content | TEXT | NOT NULL | Message content |
| is_read | BOOLEAN | DEFAULT FALSE | Whether message has been read |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### FamilySettings
Stores settings for each family.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| family_id | INTEGER | FOREIGN KEY, NOT NULL, UNIQUE | Reference to Families table |
| time_zone | VARCHAR(50) | DEFAULT 'UTC' | Family time zone |
| notification_preferences | JSON | NULL | JSON of notification settings |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

## Entity Relationship Diagram
