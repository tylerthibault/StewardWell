---
applyTo: '**'
---
# StewardWell Style Guide

## Brand Identity

### Colors

#### Primary Colors
- **Family Blue**: #1E88E5 - Main brand color representing trust and stability
- **Growth Green**: #43A047 - Represents growth, progress, and prosperity
- **Nurturing Coral**: #FF7043 - Represents nurturing, warmth, and care

#### Secondary Colors
- **Calm Teal**: #26A69A - Secondary accent for wealth module
- **Soft Purple**: #7E57C2 - Secondary accent for relationship module
- **Warm Yellow**: #FFC107 - Secondary accent for chore module

#### Neutral Colors
- **Dark Gray**: #424242 - Primary text color
- **Medium Gray**: #757575 - Secondary text color
- **Light Gray**: #EEEEEE - Background, borders
- **White**: #FFFFFF - Backgrounds, cards

### Typography

#### Headings
- **Font Family**: 'Nunito', sans-serif
- **Weights**: Bold (700) for primary headings, Semi-Bold (600) for secondary
- **Sizes**:
  - H1: 2.5rem (40px)
  - H2: 2rem (32px)
  - H3: 1.5rem (24px)
  - H4: 1.25rem (20px)
  - H5: 1rem (16px)

#### Body Text
- **Font Family**: 'Open Sans', sans-serif
- **Weight**: Regular (400), Bold (700) for emphasis
- **Size**: 1rem (16px) for standard text, 0.875rem (14px) for secondary text

#### Child Interface
- **Font Family**: 'Comic Neue', cursive (for child-specific elements)
- **Weight**: Regular (400), Bold (700)
- **Size**: 1.125rem (18px) for better readability

### Icons & Graphics

- Use rounded, friendly icons from the Material Design icon set
- Module-specific iconography:
  - Chores: Task/checklist themed icons
  - Wealth: Money/savings themed icons
  - WeTree: Heart/relationship themed icons

## UI Components

### Button Styles

#### Primary Button
- Background: Family Blue (#1E88E5)
- Text: White (#FFFFFF)
- Border: None
- Border-radius: 8px
- Padding: 10px 16px
- Hover: Darker blue (#1565C0)

#### Secondary Button
- Background: White (#FFFFFF)
- Text: Family Blue (#1E88E5)
- Border: 1px solid Family Blue
- Border-radius: 8px
- Padding: 10px 16px
- Hover: Light blue background (#E3F2FD)

#### Success Button
- Background: Growth Green (#43A047)
- Text: White (#FFFFFF)
- Border: None
- Border-radius: 8px
- Padding: 10px 16px
- Hover: Darker green (#2E7D32)

#### Delete/Danger Button
- Background: #F44336
- Text: White (#FFFFFF)
- Border: None
- Border-radius: 8px
- Padding: 10px 16px
- Hover: Darker red (#D32F2F)

#### Child Interface Buttons
- Larger (padding: 12px 20px)
- More rounded (border-radius: 12px)
- Brighter colors
- Include icons where possible

### Card Style
- Background: White (#FFFFFF)
- Border: None
- Border-radius: 12px
- Box-shadow: 0 2px 4px rgba(0,0,0,0.1)
- Padding: 20px
- Margin: 16px 0

### Form Elements

#### Inputs
- Border: 1px solid Light Gray (#EEEEEE)
- Border-radius: 6px
- Padding: 10px 12px
- Focus: Border color Family Blue (#1E88E5), light blue box shadow
- Font: Open Sans, 1rem
- Placeholder color: Medium Gray (#757575)

#### Dropdown/Select
- Same styling as inputs
- Custom chevron icon for dropdown indicator
- Hover: Light gray background (#F5F5F5)

#### Checkbox/Radio
- Custom styled with brand colors
- Animation on toggle
- Clear focus state

### Navigation

#### Top Navigation (Parent Interface)
- Background: White (#FFFFFF)
- Border-bottom: 1px solid Light Gray (#EEEEEE)
- Text: Dark Gray (#424242)
- Active item: Family Blue (#1E88E5)
- Height: 64px

#### Side Navigation (Dashboard)
- Background: White (#FFFFFF)
- Width: 240px (desktop), collapsible on mobile
- Text: Dark Gray (#424242)
- Active item: Family Blue background (#E3F2FD), Family Blue text (#1E88E5)
- Section headers: Medium Gray (#757575), uppercase, 12px

#### Child Navigation
- Larger elements
- More colorful
- Icon-focused for non-readers
- Simplified options

## Layout Guidelines

### Grid System
- Bootstrap 5 grid system (12 columns)
- Consistent gutters (1.5rem)
- Responsive breakpoints:
  - Extra small: < 576px
  - Small: ≥ 576px
  - Medium: ≥ 768px
  - Large: ≥ 992px
  - Extra large: ≥ 1200px

### Spacing
- Base unit: 4px
- Common spacing:
  - Tiny: 4px
  - Small: 8px
  - Medium: 16px
  - Large: 24px
  - Extra large: 32px
  - Huge: 48px

### Responsive Behavior
- Mobile-first approach
- Collapsible sidebars on smaller screens
- Stacked layout for mobile vs side-by-side for desktop
- Appropriate font-size adjustments for readability
- Touch-friendly tap targets (min 44px) on mobile

## Module-Specific Styling

### Chores Module
- Primary color: Warm Yellow (#FFC107)
- Icons: Task/checklist themed
- Special components: Task cards, completion trackers

### Wealth Module
- Primary color: Calm Teal (#26A69A)
- Icons: Money/savings themed
- Special components: Progress bars, goal trackers

### WeTree Module
- Primary color: Soft Purple (#7E57C2)
- Icons: Heart/relationship themed
- Special components: Calendar, milestone markers

## Accessibility Guidelines

- Maintain AA WCAG 2.1 compliance
- Minimum contrast ratio of 4.5:1 for text
- Focus states visible for keyboard navigation
- Alt text for all images
- ARIA attributes where appropriate
- Ensure all functionality is available via keyboard
- Child interface should be intuitive and not rely solely on text

## Animation & Transitions

- Keep animations subtle and purposeful
- Standard transition: 0.2s ease-out
- Avoid animations that block user interaction
- Consider reduced motion preferences
- More playful animations appropriate for child interface

## Code Style

### CSS/SCSS
- Use BEM (Block Element Modifier) naming convention
- Organize styles by component
- Use variables for colors, spacing, and typography
- Comment sections clearly

### JavaScript
- Follow ESLint recommended rules
- Use camelCase for variables and functions
- Use ES6+ features when appropriate
- Consistent error handling
- Comment complex logic

### Templates
- Maintain consistent indentation
- Keep logic in controllers, not templates
- Reuse components through includes/partials
- Comment non-obvious template blocks