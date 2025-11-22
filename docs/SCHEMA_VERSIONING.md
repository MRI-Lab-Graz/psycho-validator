# Schema Versioning System

## Overview
The prism-validator includes a schema versioning system to handle the evolution of metadata schemas over time.

## Semantic Versioning
Schemas follow semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR (e.g., 2.0.0): Breaking changes - incompatible with previous versions
- MINOR (e.g., 1.1.0): New features - backward compatible additions
- PATCH (e.g., 1.0.1): Bug fixes - backward compatible corrections

## Schema Structure
Each schema includes version metadata:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://prism-validator.org/schemas/image/v1.0.0",
  "version": "1.0.0",
  "title": "Image Stimulus Metadata"
}
```

## Metadata Requirements
All stimulus metadata must include a SchemaVersion field:

```json
{
  "Technical": {},
  "Study": {},
  "Categories": {},
  "Metadata": {
    "SchemaVersion": "1.0.0",
    "CreationDate": "2024-01-15",
    "Creator": "Research Team"
  }
}
```

## CLI Features
- List versions: `python prism-validator.py --list-versions`
- Schema info: `python prism-validator.py --schema-info image`
- Check compatibility: `python prism-validator.py --check-compatibility 1.0.1 1.0.0`

## Compatibility Rules
- Compatible: Same major version, schema version >= required version
- Patch updates: Always compatible
- Minor updates: May add new required fields (not compatible)
- Major updates: Breaking changes allowed

## Migration Strategy
1. Patch updates: Bug fixes only
2. Minor updates: Add optional fields
3. Major updates: Breaking changes; provide migration tools

## Future Considerations
- Schema migration utilities
- Warnings for deprecated fields
- Automatic schema update suggestions
- Version-specific validation rules
