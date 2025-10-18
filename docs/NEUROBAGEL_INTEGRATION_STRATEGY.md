# NeuroBagel Integration Strategy

## Current State (v1 - Simple)
- Basic dropdown with field names (participant_id, age, sex, etc.)
- Inserts flat description text into textareas
- ❌ Not aligned with NeuroBagel's sophisticated annotation model

## Target State (v2 - Hierarchical, like NeuroBagel Annotation Tool)

Follow the **NeuroBagel annotation tool** workflow:
https://neurobagel.org/user_guide/annotation_tool/

### Three-Level Annotation Strategy

#### Level 1: Column Metadata
For each column (e.g., "sex", "age", "participant_id"):
- **Description**: What this column represents
- **Data Type**: Categorical, Continuous, or Text
- **Standardized Variable**: Map to NeuroBagel harmonized variable (e.g., "biological_sex")
- **MissingValues**: How missing values are encoded

#### Level 2: Value Annotation (for Categorical Columns)
For each unique value in a categorical column:
- **Free-form Label**: e.g., "Female", "Male"
- **Description**: e.g., "Biological female sex"
- **Standardized Term**: Link to controlled vocabulary (e.g., SNOMED/UBERON URI)
- **TermURL**: Machine-readable identifier

#### Level 3: Hierarchical Organization
UI Structure:
```
📋 Participants Annotation
├── Standardized Variables (sidebar)
│   ├── Biological Sex
│   │   ├── sex (column)
│   ├── Age
│   │   ├── age (column)
│   └── ...
├── Unannotated Columns
│   ├── group
│   └── handedness
└── Main Area
    └── [Current Column Editor]
        ├── Column Metadata
        ├── Value Annotations (for categorical)
        │   ├── F → Female → standardized_uri
        │   ├── M → Male → standardized_uri
        │   └── O → Other → standardized_uri
        └── Missing Value Rules
```

## Implementation Plan

### Phase 1: Backend (Fetch Augmented Data)
1. Extend `/api/neurobagel/participants` endpoint to return:
   - Column descriptions + data types
   - Standardized variable mappings
   - Categorical value enumerations with URIs
   - Example: `age: {type: "continuous", description: "...", unit: "years"}`
   - Example: `sex: {type: "categorical", levels: {F: {label: "Female", uri: "..."}, M: {...}}}`

2. Data source: https://neurobagel.org/data_models/dictionaries/participants.json
   - Already contains structured metadata + categorical value vocabularies
   - May need to normalize/augment with standardized variable mappings

### Phase 2: Frontend UI (Hierarchical Annotation Widget)
1. **Sidebar**: Group columns by standardized variable
   - Click a variable to show its columns
   - Click a column to edit its metadata & values

2. **Main Area: Column Editor**
   - Tab 1: Column Metadata
     - Text input: Description
     - Dropdown: Data Type (Categorical / Continuous / Text)
     - Dropdown: Standardized Variable (with search)
   
   - Tab 2: Value Annotations (only for Categorical)
     - For each unique value from participants.json:
       - Show current value
       - Input: Free-form label + description
       - Dropdown: Standardized term from vocabulary
       - Display: URI/identifier
       - Checkbox: Mark as missing
   
   - Tab 3: Column Settings
     - Missing value symbols/rules

3. **Controls**
   - "Apply to All" button for quick standardization
   - "Copy from Template" to reuse annotations
   - "Validate" button to check completeness

### Phase 3: Integration with Existing JSON Editor
1. When editing `participants.json` in the web editor:
   - Add a new tab/panel: "NeuroBagel Annotation"
   - Keep existing JSON editor as "Raw JSON" tab
   - Show side-by-side: annotation UI + generated JSON preview

2. Sync mechanism:
   - Annotation changes update the JSON
   - JSON changes parse back to annotation UI (if valid)

## Data Structure Example

### Input (participants.json from BIDS)
```json
{
  "age": {
    "Description": "Age of the participant",
    "Units": "years"
  },
  "sex": {
    "Description": "Biological sex of participant",
    "Levels": {
      "M": "male",
      "F": "female"
    }
  }
}
```

### Augmented Output (from NeuroBagel API)
```json
{
  "age": {
    "description": "Age of participant",
    "data_type": "continuous",
    "standardized_variable": "age",
    "unit": "years",
    "min": 0,
    "max": 120
  },
  "sex": {
    "description": "Biological sex of participant",
    "data_type": "categorical",
    "standardized_variable": "biological_sex",
    "levels": {
      "M": {
        "label": "Male",
        "description": "Male sex",
        "standardized_uri": "http://purl.obolibrary.org/obo/PATO_0000384"
      },
      "F": {
        "label": "Female", 
        "description": "Female sex",
        "standardized_uri": "http://purl.obolibrary.org/obo/PATO_0000383"
      }
    }
  }
}
```

## Benefits of This Approach

✅ **FAIR Compliance**: Standardized URIs make data discoverable & reusable
✅ **Data Harmonization**: Map local values to standardized vocabularies
✅ **NeuroBagel Compatible**: Output can be used by downstream NeuroBagel tools
✅ **User-Friendly**: Hierarchical UI mimics NeuroBagel's established workflow
✅ **Validation Ready**: Can check completeness before export
✅ **Incremental**: Users can annotate columns progressively

## Next Steps

1. Check NeuroBagel's actual dictionary structure (https://neurobagel.org/data_models/dictionaries/)
2. Design data model for augmented annotations
3. Implement backend fetch + data transformation
4. Build hierarchical UI widget
5. Integrate with existing JSON editor
6. Test with real BIDS datasets

