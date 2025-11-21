# BIDS Compatibility Assessment

## Executive Summary
The current schema implementation is **partially compatible** with BIDS. While it enforces BIDS-compliant filenames and directory structures, the JSON sidecar schemas are **structurally incompatible** with standard BIDS sidecars.

## Detailed Analysis

### 1. Filename Compatibility (✅ Compatible)
The validator (`src/validator.py`) enforces BIDS-style naming conventions:
- **Pattern**: `sub-[label]_ses-[label]_task-[label]_run-[index]`
- **Extensions**: Correctly handles `.nii.gz`, `.tsv`, `.edf`, etc.
- **Logic**: The `BIDS_REGEX` in `validator.py` aligns with BIDS principles.

### 2. JSON Sidecar Compatibility (❌ Incompatible Structure)
Standard BIDS JSON sidecars use a **flat structure** with specific CamelCase keys. The current schemas enforce a **nested structure**.

**Example: EEG Sidecar**

| Feature | Standard BIDS (`_eeg.json`) | Current Schema (`eeg.schema.json`) |
|---------|-----------------------------|------------------------------------|
| **Structure** | Flat (Root level keys) | Nested (`Technical`, `Study`, `Metadata`) |
| **Sampling Rate** | `SamplingFrequency` | `Technical.SamplingRate` |
| **Manufacturer** | `Manufacturer` | `Metadata.Equipment.Manufacturer` |
| **Task Name** | `TaskName` | `Study.Task` |

**Impact**: A valid BIDS dataset imported into this system will fail validation because the JSON sidecars do not match the expected nested schema structure. Conversely, a dataset created with this system will have sidecars that are not valid BIDS (due to nesting and custom keys).

### 3. Dataset Description (⚠️ Partial Match)
The `dataset_description.schema.json` is closer to BIDS but still has differences:
- **Authors**: BIDS expects an array of strings. The schema allows objects (richer metadata), which might cause warnings in strict BIDS validators.
- **Funding**: BIDS expects an array of strings. The schema uses objects.
- **Extra Fields**: The schema includes `EthicsApprovals`, `Publications`, etc., which are allowed in BIDS (as extra fields) but not standard.

## Recommendations

To achieve full BIDS compatibility, we have two options:

### Option A: Flatten the Schemas (Recommended for BIDS Interoperability)
Modify the schemas to match the flat BIDS structure.
- Remove top-level nesting (`Technical`, `Study`, etc.).
- Rename keys to match BIDS specification (e.g., `SamplingRate` -> `SamplingFrequency`).
- Use BIDS-standard enums where applicable.

### Option B: Implement a Mapping Layer
Keep the rich, nested internal schema but add a translation layer:
- **Import**: Convert flat BIDS JSON to nested internal format.
- **Export**: Flatten internal format to standard BIDS JSON.

## Conclusion
The system currently operates as a "BIDS-inspired" validator rather than a strict BIDS validator. To allow standard BIDS data, the schemas must be adjusted or a conversion adapter must be implemented.
