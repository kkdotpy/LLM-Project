# FoodKeeper Data Description

## Overview

This dataset comes from the **USDA FSIS FoodKeeper** application, which provides consumer advice on safe food storage, cooking temperatures, and preparation methods.

**Total Original Records:** 868 rows across 4 sheets


## Part 1: Original Source Data (4 Sheets)

### Sheet 1: Categories (25 rows)
A lookup table for food categories.

| Field | Description | Example |
|-------|-------------|---------|
| `ID` | Unique category identifier | 7.0 |
| `Category_Name` | Name of the food category | "Dairy Products & Eggs" |
| `Subcategory_Name` | More specific grouping (can be null) | "Bakery", "Fresh" |

**Purpose:** Groups products into categories like Meat, Dairy, Baked Goods, etc.



### Sheet 2: Products (661 rows)
Main product information with storage times.

| Field | Description | Example |
|-------|-------------|---------|
| `ID` | Unique product identifier | 1.0 |
| `Category_ID` | Links to Categories sheet | 7.0 |
| `Name` | Food name | "Butter" |
| `Keywords` | Searchable terms (includes cuts/varieties) | "Beef,rib roast,boneless" |
| `Pantry_tips` | Room temperature storage advice | "May be left at room temperature for 1-2 days" |
| `DOP_Refrigerate_Min` | Minimum days from purchase | 1.0 |
| `DOP_Refrigerate_Max` | Maximum days from purchase | 2.0 |
| `DOP_Refrigerate_Metric` | Unit of time | "Months", "Weeks", "Days" |
| `Refrigerate_After_Opening_Min` | Minimum days after opening | 3.0 |
| `Refrigerate_After_Opening_Max` | Maximum days after opening | 4.0 |
| `Refrigerate_After_Opening_Metric` | Unit of time | "Weeks" |

**Purpose:** Answers "How long does X last?" and "Where should I store X?"



### Sheet 3: Safety (93 rows)
Safe cooking temperatures and handling instructions.

| Field | Description | Example |
|-------|-------------|---------|
| `ID` | Unique safety record identifier | 3.0 |
| `Product_ID` | Links to Products sheet | 34.0 |
| `Tips` | Safety handling advice | "Cook until yolk and white are firm" |
| `Safe_Minimum_Temperature` | Minimum safe internal temp (°F) | 145.0 |
| `Rest_Time` | Minutes to rest after cooking | 3.0 |
| `Rest_Time_metric` | Unit of rest time | "minutes" |

**Purpose:** Answers "What temperature should I cook X to?" and food safety questions.

---

### Sheet 4: Cooking (89 rows)
Specific cooking methods, temperatures, and timing instructions.

| Field | Description | Example |
|-------|-------------|---------|
| `ID` | Unique cooking record identifier | 1.0 |
| `Product_ID` | Links to Products sheet | 34.0 |
| `Cooking_Method` | Preparation method | "Oven", "Braise", "Grill" |
| `Cooking_Temperature` | Cooking temperature in °F | 325.0 or "425-450" |
| `Measure_from` | Minimum size/weight | 4.0 |
| `Measure_to` | Maximum size/weight | 8.0 |
| `Size_metric` | Unit of measurement | "pounds", "inches", "ounces" |
| `Timing_from` | Minimum cooking time | 23.0 |
| `Timing_to` | Maximum cooking time | 30.0 |
| `Timing_metric` | Time unit | "minutes", "hours" |
| `Timing_per` | If time is per unit (e.g., per pound) | "pound" |

**Purpose:** Answers "How do I cook X?" with specific method, temperature, and timing.



## Part 2: Data Relationships

```
Categories (ID) ─────┐
                     │
                     ▼
Products (Category_ID) ─────┐
                            │
                            ▼
                       Safety (Product_ID)
                            │
                            ▼
                      Cooking (Product_ID)
```

**Key Points:**
- One Category → Many Products
- One Product → Zero or One Safety record
- One Product → Zero or More Cooking records (different cuts/methods)



## Part 3: Processed RAG Collections (3 JSONL Files)

The original 4 sheets were joined and processed into 3 JSONL collections. Variety information (e.g., "Rib Roast" for Beef) was extracted from the Keywords field.



### Collection 1: Storage (rag_storage.jsonl)

**Size:** 388 documents

**Document Structure:**
```json
{
  "id": "storage_34.0",
  "food_name": "Beef (Rib Roast)",
  "category": "Meat",
  "subcategory": "Fresh",
  "content": "Beef (Rib Roast). Refrigerator (from purchase): 3-5 Days",
  "type": "storage"
}
```

**Fields:**
| Field | Description |
|-------|-------------|
| `id` | "storage_" + Product_ID |
| `food_name` | Food name with cut/variety (e.g., "Beef (Rib Roast)") |
| `category` | Food category from Categories table |
| `subcategory` | More specific grouping |
| `content` | Natural language storage instructions |
| `type` | Always "storage" |

**Content Examples:**
- `Butter. Pantry: May be left at room temperature for 1-2 days | Refrigerator (from purchase): 1-2 Months`
- `Cheese (Cheddar). Refrigerator (from purchase): 6 Months | Refrigerator (after opening): 3-4 Weeks`
- `Beef (Ground). Refrigerator (from purchase): 1-2 Days`

**Answers Questions Like:**
- "How long does butter last in the fridge?"
- "Can I leave cheese at room temperature?"
- "How long does ground beef last after opening?"



### Collection 2: Safety (rag_safety.jsonl)

**Size:** 91 documents

**Document Structure:**
```json
{
  "id": "safety_34.0",
  "food_name": "Beef (Rib Roast)",
  "content": "Beef (Rib Roast). Cook to 145°F | Rest for 3 minutes",
  "type": "safety"
}
```

**Fields:**
| Field | Description |
|-------|-------------|
| `id` | "safety_" + Product_ID |
| `food_name` | Food name with cut/variety |
| `content` | Natural language safety instructions |
| `type` | Always "safety" |

**Content Examples:**
- `Eggs. Tip: Cook until yolk and white are firm`
- `Beef (Ground). Cook to 160°F`
- `Beef (Steak). Cook to 145°F | Rest for 3 minutes`

**Answers Questions Like:**
- "What temperature should I cook chicken to?"
- "Is pork done at 145°F?"
- "How long should beef rest after cooking?"


### Collection 3: Cooking (rag_cooking.jsonl)

**Size:** 88 documents

**Document Structure:**
```json
{
  "id": "cooking_34.0",
  "food_name": "Beef (Rib Roast)",
  "content": "Beef (Rib Roast). Method: Oven | Temperature: 325°F | Cook 23-30 minutes per pound | For 4-8 pounds size",
  "type": "cooking"
}
```

**Fields:**
| Field | Description |
|-------|-------------|
| `id` | "cooking_" + Product_ID |
| `food_name` | Food name with cut/variety |
| `content` | Natural language cooking instructions |
| `type` | Always "cooking" |

**Content Examples:**
- `Beef (Rib Roast). Method: Oven | Temperature: 325°F | Cook 23-30 minutes per pound | For 4-8 pounds size`
- `Beef (Chuck Roast). Method: Braise | Temperature: 325°F | Cook for 1.5-2.5 hours | For 3-4 pounds size`
- `Lamb (Leg). Method: Oven | Temperature: 325°F | Cook 20-25 minutes per pound | For 5-7 pounds size`

**Answers Questions Like:**
- "How to cook a beef rib roast?"
- "What temperature for roasting lamb?"
- "How to braise short ribs?"



## Part 4: Summary

| Collection | Count | Primary Use |
|------------|-------|-------------|
| Storage | 388 | Shelf life & storage location |
| Safety | 91 | Cooking temperatures & handling |
| Cooking | 88 | Cooking methods & times |

**Food Name Enhancement Example:**
- Before: "Beef"
- After: "Beef (Rib Roast)", "Beef (Rump Roast)", "Beef (Tenderloin)", "Beef (Ground)"

**Notes:**
- `DOP` = "Date of Purchase"
- `None` = Information not available
- Decimal values (1.0) cleaned to integers (1) where possible
