# Biometrics

The `biometrics` modality is a PRISM extension designed for physiological assessments that do not fit into standard BIDS `beh` or `physio` categories. Examples include VO2max tests, plank tests, balance assessments, or anthropometric measurements.

## File Name Structure

Biometric data files MUST follow this naming convention:

`sub-<label>[_ses-<label>]_task-<label>_biometrics.<extension>`

| Entity | Description |
| --- | --- |
| `sub` | **Required**. The subject identifier. |
| `ses` | **Optional**. The session identifier. |
| `task` | **Required**. The name of the biometric task (e.g., `task-ukk`, `task-plank`). |
| `biometrics` | **Required**. The suffix indicating the modality. |
| `extension` | **Required**. Typically `.tsv`. |

**Example:**
`sub-001_ses-01_task-ukk_biometrics.tsv`

## Sidecar JSON (`*_biometrics.json`)

Each biometric data file MUST be associated with a JSON sidecar file. This file contains metadata about the assessment protocol.

### Top-Level Objects

The JSON structure is divided into three main objects to organize metadata logically.

| Object | Requirement | Description |
| --- | --- | --- |
| `Technical` | **REQUIRED** | Technical details about the data acquisition. |
| `Study` | **REQUIRED** | Scientific context, protocol details, and references. |
| `Metadata` | **REQUIRED** | Administrative metadata about the file itself. |

### `Technical` Object Fields

| Key | Requirement | Type | Description |
| --- | --- | --- | --- |
| `StimulusType` | **REQUIRED** | `string` | MUST be `"Biometrics"`. |
| `FileFormat` | **REQUIRED** | `string` | The format of the data file (e.g., `"tsv"`). |
| `Equipment` | **REQUIRED** | `string` | The device or equipment used (e.g., "Stopwatch", "Cycle Ergometer"). |
| `Supervisor` | OPTIONAL | `string` | Who supervised the test. Allowed: `"investigator"`, `"physician"`, `"trainer"`, `"self"`. |

### `Study` Object Fields

| Key | Requirement | Type | Description |
| --- | --- | --- | --- |
| `BiometricName` | **REQUIRED** | `string` | Short alphanumeric identifier (e.g., `"ukk"`). |
| `OriginalName` | **REQUIRED** | `string` | Full human-readable name (e.g., `"UKK Walk Test"`). |
| `Description` | **REQUIRED** | `string` | Detailed description of the procedure. |
| `Instructions` | RECOMMENDED | `string` | Instructions given to the participant. |
| `Protocol` | OPTIONAL | `string` | Reference to the specific protocol used. |
| `Author` | OPTIONAL | `string` | Author(s) of the test protocol. |
| `DOI` | OPTIONAL | `string` | DOI of the reference publication. |
| `Reference` | OPTIONAL | `string` | Full citation. |
| `EstimatedDuration` | OPTIONAL | `string` | Typical duration (e.g., `"15 min"`). |
| `TargetPopulation` | OPTIONAL | `string` | Intended demographic (e.g., `"Adults 18-65"`). |
| `ExclusionCriteria` | OPTIONAL | `string` | Contraindications. |

### `Metadata` Object Fields

| Key | Requirement | Type | Description |
| --- | --- | --- | --- |
| `SchemaVersion` | **REQUIRED** | `string` | Version of the schema used (e.g., `"1.0.0"`). |
| `CreationDate` | **REQUIRED** | `string` | Date of file creation in `YYYY-MM-DD` format. |
| `Creator` | OPTIONAL | `string` | Tool or person who created the file. |

## Example Sidecar

```json
{
  "Technical": {
    "StimulusType": "Biometrics",
    "FileFormat": "tsv",
    "Equipment": "Stopwatch, Heart Rate Monitor"
  },
  "Study": {
    "BiometricName": "ukk",
    "OriginalName": "UKK 2km Walk Test",
    "Description": "Participants walk 2km as fast as possible. HR and time are recorded.",
    "Instructions": "Walk 2km at a steady, fast pace. Do not run.",
    "Reference": "Oja et al. (1991)",
    "EstimatedDuration": "15-20 min"
  },
  "Metadata": {
    "SchemaVersion": "1.0.0",
    "CreationDate": "2025-11-27"
  }
}
```
