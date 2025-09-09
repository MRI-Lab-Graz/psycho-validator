# Psycho-Validator: BIDS-inspired Validation Tool

## Overview

This tool validates datasets containing psychological/psychophysical stimuli and experimental data following a BIDS-inspired structure. It's designed specifically for experiments involving multiple stimulus modalities like images, videos, audio, etc.

## Features

- **Multi-modal validation**: Supports images, movies, audio, EEG, eye-tracking, and behavioral data
- **BIDS-inspired naming**: Validates filenames follow the pattern `sub-<label>_[ses-<label>_]task-<label>_[run-<index>_]<suffix>`
- **JSON schema validation**: Validates sidecar metadata files against modality-specific schemas
- **Flexible structure**: Supports both session-based and direct subject organization
- **Comprehensive reporting**: Clear error messages with emoji indicators and exit codes

## Directory Structure

```
dataset/
├── dataset_description.json     # Required dataset metadata
├── participants.tsv            # Optional participant information
├── sub-<label>/               # Subject directories
│   ├── ses-<label>/          # Optional session directories
│   │   └── <modality>/       # Modality-specific folders
│   └── <modality>/           # Or direct modality folders
```

## Supported Modalities

| Modality | File Extensions | Required Fields |
|----------|----------------|-----------------|
| `image` | .png, .jpg, .jpeg, .tiff | StimulusType, FileFormat, Resolution, TaskName |
| `movie` | .mp4, .avi, .mov | StimulusType, FileFormat, Resolution, Duration, TaskName |
| `audio` | .wav, .mp3, .flac | StimulusType, FileFormat, SampleRate, Duration, TaskName |
| `eyetracking` | .tsv, .edf | (Schema not implemented yet) |
| `eeg` | .edf, .bdf, .eeg | (Schema not implemented yet) |
| `behavior` | .tsv | (Schema not implemented yet) |

## Schema Structure

Each stimulus file must have a corresponding `.json` sidecar file with the same basename. These JSON files contain metadata about the stimulus and are validated against JSON schemas in the `schemas/` directory.

### Example Image Metadata (`.json` sidecar):
```json
{
  "StimulusType": "Image",
  "FileFormat": "png",
  "Resolution": [800, 600],
  "ColorSpace": "RGB",
  "TaskName": "facerecognition",
  "StimulusID": "face_001",
  "PresentedWith": "PsychoPy 2023.1"
}
```

## Usage

### Basic validation:
```bash
python psycho-validator.py /path/to/dataset
```

### Verbose output:
```bash
python psycho-validator.py /path/to/dataset -v
```

### Exit codes:
- `0`: Dataset is valid
- `1`: Validation errors found

## Test Dataset

The included `test_dataset/` demonstrates:
- ✅ Valid files with proper naming and metadata
- ❌ Invalid naming conventions
- ❌ Missing sidecar files
- ✅ Mixed session/no-session structures

## Files in this Repository

- `psycho-validator.py` - Main validation script
- `schemas/` - JSON schemas for each modality
- `test_dataset/` - Example dataset for testing
- `test_validator.py` - Comprehensive test script
- `create_dummy_files.py` - Script to generate realistic test files

## Future Enhancements

1. **Additional modalities**: Add schemas for EEG, eye-tracking, and behavioral data
2. **Cross-file validation**: Validate stimulus-response timing relationships
3. **BIDS compatibility**: Ensure full compatibility with official BIDS standard
4. **Web interface**: Create a web-based validation tool
5. **Batch processing**: Support for validating multiple datasets

## Dependencies

- Python 3.6+
- `jsonschema` - For JSON schema validation

Optional (for dummy file generation):
- `Pillow` - For creating test images
- `numpy` - For generating test data
