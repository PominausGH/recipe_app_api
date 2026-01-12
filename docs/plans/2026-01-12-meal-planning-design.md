# Meal Planning Feature Design

## Overview

Add meal planning functionality to the Recipe App, allowing users to plan weekly meals, manage household members with dietary restrictions, and generate smart shopping lists.

## Scope: Standard

- Weekly meal planning with 35 slots (5 meals × 7 days)
- Manual recipe assignment + reusable templates
- Household profiles with dietary tags and conflict warnings
- Adjustable servings per meal slot
- Shopping list with smart categorization by store section
- Backend storage with frontend caching for offline viewing

---

## Data Model

### HouseholdProfile
Extends existing User model for family/group meal planning.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `household_name` | CharField | Display name for household |
| `owner` | FK (User) | User who created the household |
| `created_at` | DateTime | Creation timestamp |

### HouseholdMember
Represents people eating meals (may or may not be app users).

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField | Member's name |
| `household` | FK (Household) | Parent household |
| `dietary_tags` | M2M (DietaryTag) | Dietary restrictions |
| `is_primary` | Boolean | Primary household member |

### DietaryTag
Reuses existing recipe tag system for dietary restrictions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField | Display name (e.g., "Vegetarian") |
| `slug` | SlugField | URL-safe identifier |

Common tags: vegetarian, vegan, gluten-free, dairy-free, nut-free, shellfish-free, low-sodium, keto

### MealPlan
Weekly meal plan or reusable template.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `household` | FK (Household) | Owning household |
| `week_start_date` | DateField | Monday of the plan week (null for templates) |
| `name` | CharField | Optional name (required for templates) |
| `is_template` | Boolean | Whether this is a reusable template |
| `created_by` | FK (User) | User who created the plan |
| `created_at` | DateTime | Creation timestamp |

### MealSlot
Individual meal slot within a plan (35 per plan).

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `meal_plan` | FK (MealPlan) | Parent meal plan |
| `day_of_week` | Integer | 0 (Monday) through 6 (Sunday) |
| `meal_type` | CharField | breakfast, lunch, dinner, snack1, snack2 |
| `recipe` | FK (Recipe) | Assigned recipe (nullable) |
| `servings` | Integer | Number of servings (default: recipe default) |

### Ingredient Category Extension
Add category field to existing Ingredient model.

| Field | Type | Description |
|-------|------|-------------|
| `category` | CharField | Store section for shopping list grouping |

---

## API Endpoints

### Household Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/household/` | Create household |
| `GET` | `/api/household/` | Get user's household |
| `POST` | `/api/household/members/` | Add member |
| `PATCH` | `/api/household/members/{id}/` | Update member |
| `DELETE` | `/api/household/members/{id}/` | Remove member |

### Meal Plans

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/meal-plans/` | List plans (filter: `?week=2026-01-13` or `?templates=true`) |
| `POST` | `/api/meal-plans/` | Create new plan |
| `GET` | `/api/meal-plans/{id}/` | Get plan with all 35 slots |
| `DELETE` | `/api/meal-plans/{id}/` | Delete plan |

### Meal Slots

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PATCH` | `/api/meal-plans/{plan_id}/slots/{slot_id}/` | Assign recipe, set servings |
| `POST` | `/api/meal-plans/{plan_id}/slots/bulk/` | Update multiple slots |
| `DELETE` | `/api/meal-plans/{plan_id}/slots/{slot_id}/recipe/` | Clear slot |

### Shopping List

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/meal-plans/{id}/shopping-list/` | Generate categorized shopping list |

### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/meal-plans/{id}/save-as-template/` | Save plan as template |
| `POST` | `/api/meal-plans/from-template/{template_id}/` | Create plan from template |

---

## Shopping List Logic

### Ingredient Aggregation
1. Collect all ingredients from recipes in the meal plan
2. Scale quantities by servings per slot (recipe serves 4, slot set to 6 → multiply by 1.5)
3. Merge duplicates by ingredient name + unit (e.g., "2 onions" + "1 onion" → "3 onions")
4. Handle unit conversion where possible (500g + 1kg → 1.5kg)

### Store Categories
```
- Produce (fruits, vegetables, herbs)
- Meat & Seafood
- Dairy & Eggs
- Bakery
- Frozen
- Pantry (canned goods, pasta, rice, oils)
- Spices & Seasonings
- Beverages
- Other
```

### Categorization Approach
- Add `category` field to Ingredient model
- New ingredients default to "Other", updated via admin
- Shopping list groups by category, sorted alphabetically within each

### Response Format
```json
{
  "categories": [
    {
      "name": "Produce",
      "items": [
        {"ingredient": "Onion", "quantity": 3, "unit": "whole"},
        {"ingredient": "Garlic", "quantity": 6, "unit": "cloves"}
      ]
    }
  ],
  "warnings": ["Missing quantity for: salt, pepper"]
}
```

---

## Frontend Pages & Components

### New Pages

#### `/meal-plan` - Main Meal Planning Page
- Week selector (prev/next arrows, date picker)
- 7-column grid showing each day
- Each day shows 5 meal slots (Breakfast → Snack 2)
- Empty slots show "+" button, filled slots show recipe card thumbnail
- "Generate Shopping List" button
- "Save as Template" button

#### `/meal-plan/templates` - Template Management
- List of saved templates with names
- "Use Template" applies it to current week
- Delete/rename template options

#### `/household` - Household Settings
- Create/manage household
- Add/edit/remove members
- Assign dietary tags per member

#### `/shopping-list` - Shopping List View
- Categorized ingredient list
- Checkboxes to mark items as "got it"
- Print/share functionality
- Dietary conflict warnings banner at top

### Key Components

| Component | Description |
|-----------|-------------|
| `MealSlotCard` | Recipe thumbnail, name, servings adjuster |
| `RecipePickerModal` | Search/browse recipes to assign to slot |
| `WeekNavigator` | Week selection controls |
| `ShoppingListCategory` | Collapsible category with items |
| `HouseholdMemberCard` | Member with dietary tag chips |
| `DietaryWarningBanner` | Alerts when meals conflict with restrictions |

---

## Frontend State & Caching

### State Management (React Context)

#### `MealPlanContext`
- Holds current week's plan, slots, and loading state
- Provides actions: `assignRecipe`, `updateServings`, `clearSlot`
- Caches current week in localStorage

#### `HouseholdContext`
- Holds household info and members
- Provides actions: `addMember`, `updateMember`, `removeMember`

### Local Caching Strategy
```
localStorage keys:
  - mealplan_week_{date}: Full plan data for that week
  - mealplan_templates: List of template summaries
  - household: Household and members data
```

- On page load: Show cached data immediately, fetch fresh in background
- On mutation: Update server first, then update cache on success
- Cache expiry: Refresh if data older than 1 hour
- Offline: Read-only mode, show "offline" indicator

### API Integration
- New `api/mealPlan.js` service file
- New `api/household.js` service file
- Uses existing `apiClient` with auth headers

### Optimistic Updates
- Slot assignments update UI immediately
- Revert on API failure with error toast

---

## Error Handling & Edge Cases

### API Errors
| Error | Handling |
|-------|----------|
| Network failure | Toast "Unable to save. Check your connection." + revert |
| 401 Unauthorized | Redirect to login |
| 404 Plan not found | Redirect to `/meal-plan` with message |
| 400 Validation error | Show field errors inline |

### Business Logic Errors
| Scenario | Handling |
|----------|----------|
| Recipe deleted while in plan | Slot shows "Recipe unavailable" with picker option |
| Template deleted while viewing | Toast notification, refresh list |
| Duplicate plan for same week | API returns existing plan |

### Dietary Conflict Warnings
- Non-blocking: Plan saves, warning banner displays
- Format: "Chicken Parmesan contains dairy - conflicts with Emma (dairy-free)"
- Shown on meal plan page and shopping list page
- User can dismiss warnings per session

### Edge Cases
| Case | Handling |
|------|----------|
| Empty meal plan | Shopping list shows "No recipes added yet" |
| Recipe with missing ingredients | Warnings array notes incomplete data |
| Servings set to 0 | Excluded from shopping list |
| Week boundary | Plans are Monday-Sunday |

### Loading States
- Skeleton loaders for meal plan grid
- Spinner on recipe picker search
- Disabled buttons during save operations

---

## Testing Strategy

### Backend Tests (pytest)

#### Unit Tests
- `test_shopping_list_aggregation` - Quantities merge correctly
- `test_shopping_list_scaling` - Servings multiplier works
- `test_unit_conversion` - g/kg, ml/l conversions
- `test_dietary_conflict_detection` - Warnings generated correctly
- `test_template_creation` - Plan saves as template without week_start_date

#### API Tests
- `test_create_meal_plan` - Returns 35 empty slots
- `test_assign_recipe_to_slot` - Slot updates, returns dietary warnings
- `test_bulk_slot_update` - Multiple slots in one request
- `test_shopping_list_generation` - Categorized response format
- `test_household_member_crud` - Create, update, delete members
- `test_plan_from_template` - Template copies correctly to new week

#### Permission Tests
- `test_cannot_access_other_household_plan`
- `test_only_owner_can_delete_household`

### Frontend Tests (Vitest + React Testing Library)

#### Component Tests
- `MealSlotCard` - Renders recipe, servings adjuster works
- `RecipePickerModal` - Search filters, selection callback fires
- `ShoppingListCategory` - Expands/collapses, checkboxes toggle
- `DietaryWarningBanner` - Displays conflicts, dismissible

#### Integration Tests
- Assign recipe flow: open picker → search → select → slot updates
- Shopping list generation: populated plan → click generate → list displays

---

## File Structure

### Backend (app/mealplan/)
```
app/mealplan/
├── __init__.py
├── models.py          # MealPlan, MealSlot, Household models
├── serializers.py     # DRF serializers
├── views.py           # ViewSets for all endpoints
├── urls.py            # URL routing
├── services.py        # Shopping list generation logic
├── admin.py           # Admin interface
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_api.py
    └── test_services.py
```

### Frontend (frontend/src/)
```
frontend/src/
├── pages/
│   ├── MealPlan.jsx
│   ├── MealPlanTemplates.jsx
│   ├── ShoppingList.jsx
│   └── Household.jsx
├── components/
│   └── mealplan/
│       ├── MealSlotCard.jsx
│       ├── RecipePickerModal.jsx
│       ├── WeekNavigator.jsx
│       ├── ShoppingListCategory.jsx
│       ├── HouseholdMemberCard.jsx
│       └── DietaryWarningBanner.jsx
├── contexts/
│   ├── MealPlanContext.jsx
│   └── HouseholdContext.jsx
└── api/
    ├── mealPlan.js
    └── household.js
```
