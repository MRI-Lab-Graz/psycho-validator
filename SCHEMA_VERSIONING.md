# Schema Versioning System

## Overview
The psycho-validator now includes a comprehensive schema versioning system to handle the evolution of metadata schemas over time. This is essential for long-term institutional use where schemas may need to be updated while maintaining backward compatibility.

## Semantic Versioning
Schemas follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (e.g., 2.0.0): Breaking changes - incompatible with previous versions
- **MINOR** (e.g., 1.1.0): New features - backward compatible additions  
- **PATCH** (e.g., 1.0.1): Bug fixes - backward compatible corrections

## Schema Structure
Each schema now includes version metadata:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://psycho-validator.org/schemas/image/v1.0.0",
  "version": "1.0.0",
  "title": "Image Stimulus Metadata",
  ...
}
```

## Metadata Requirements
All stimulus metadata must include a SchemaVersion field:

```json
{
  "Technical": { ... },
  "Study": { ... },
  "Categories": { ... },
  "Metadata": {
    "SchemaVersion": "1.0.0",
    "CreationDate": "2024-01-15",
    "Creator": "Research Team"
  }
}
```

## Command Line Features

### List Available Schemas
```bash
python psycho-validator.py --list-versions
```

### View Schema Details
```bash
python psycho-validator.py --schema-info image
```

### Check Version Compatibility
```bash
python psycho-validator.py --check-compatibility 1.0.1 1.0.0
```

## Compatibility Rules
- **Compatible**: Same major version, schema version >= required version
- **Patch updates** (1.0.1 vs 1.0.0): Always compatible
- **Minor updates** (1.1.0 vs 1.0.0): Not compatible (may have new required fields)
- **Major updates** (2.0.0 vs 1.0.0): Not compatible (breaking changes)

## Migration Strategy
When updating schemas:

1. **Patch updates**: Bug fixes only, no new requirements
2. **Minor updates**: Add optional fields, maintain backward compatibility  
3. **Major updates**: Breaking changes allowed, provide migration tools

## Future Considerations
- Schema migration utilities for major version changes
- Validation warnings for deprecated fields
- Automatic schema update suggestions
- Version-specific validation rules

## Example Usage
```bash
# Generate test data with current schema version
python create_dummy_files.py

# Validate with version checking
python psycho-validator.py consistent_test_dataset/

# Run comprehensive schema versioning demo
python demo_schema_versioning.py
```

## Benefits
- **Future-proofing**: Handle schema evolution gracefully
- **Institutional compliance**: Track metadata standard versions
- **Quality assurance**: Ensure data consistency across time periods
- **Collaboration**: Clear versioning for multi-site studies
- **Automation**: Programmatic version compatibility checking
