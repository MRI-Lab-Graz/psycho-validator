# Prism-Validator: BIDS-inspired Validation Tool

## 🚀 Quick Start

**👉 Run the web interface** (recommended for all users):

```bash
bash setup.sh              # One-time setup (macOS/Linux)
python prism-validator-web.py
```

The web interface will open automatically at `http://localhost:5001`. No additional configuration needed!

---

## Overview

Prism-Validator validates datasets containing psychological/psychophysical stimuli and experimental data following a BIDS-inspired structure. It's designed specifically for experiments involving multiple stimulus modalities like images, videos, audio, etc.

## ✨ Key Features

### 🎯 Web Interface (Primary Method)
- **Drag & drop dataset upload** - Just drop a folder or ZIP file
- **Interactive validation** - Real-time results with visual charts
- **🧠 NeuroBagel Integration** - Annotate participants with standardized ontologies
  - Professional annotation widget for participant metadata
  - Integration with official NeuroBagel dictionary
  - SNOMED-CT shorthand URI support
  - Auto-detect and parse participants.tsv files
  - Categorical value extraction and labeling
- **JSON Editor** - Edit and create metadata files interactively
- **Local processing** - All data stays on your machine (no cloud uploads)
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Responsive design** - Works on desktop and mobile browsers

### ✅ Validation Features
- **Multi-modal validation**: Supports images, movies, audio, EEG, eye-tracking, and behavioral data
- **BIDS-App Compatibility**: Automatically updates `.bidsignore` to ensure custom modalities (like `image/`, `movie/`) are ignored by standard BIDS tools (e.g., fMRIPrep), preventing crashes.
- **BIDS-inspired naming**: Validates filenames follow the pattern `sub-<label>_[ses-<label>_]task-<label>_[run-<index>_]<suffix>`
- **JSON schema validation**: Validates sidecar metadata against modality-specific schemas
- **Schema versioning**: Multiple schema versions (stable, v0.1, etc.) selectable in UI
- **Flexible structure**: Supports both session-based and direct subject organization
- **Cross-subject consistency**: Warns when subjects have inconsistent modalities or tasks
- **Comprehensive reporting**: 
  - Dataset summary with subject/session counts
  - Modality breakdown with file counts
  - Task detection and listing
  - File statistics (data files vs sidecars)
  - Cross-subject consistency warnings
  - Clear error and warning categorization

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
python prism-validator.py /path/to/dataset
```

### Verbose output (shows scanning details):
```bash
python prism-validator.py /path/to/dataset -v
```

### Example Output:

For a valid dataset:
```
🔍 Validating dataset: valid_test_dataset/

============================================================
🗂️  DATASET SUMMARY
============================================================
📁 Dataset: valid_test_dataset
👥 Subjects: 2
📋 Sessions: No session structure detected

🎯 MODALITIES (2 found):
  ✅ audio: 2 files
  ✅ image: 2 files

📝 TASKS (2 found):
  • listening
  • recognition

📄 FILES:
  • Data files: 2
  • Sidecar files: 2
  • Total files: 4

============================================================
✅ VALIDATION RESULTS
============================================================
🎉 No issues found! Dataset is valid.
```

For a dataset with issues:
```
============================================================
🔍 VALIDATION RESULTS
============================================================

🔴 ERRORS (1):
   1. Missing sidecar for test_dataset/sub-003/image/invalid-file.jpg

� WARNINGS (3):
   1. Subject sub-003 session ses-001 missing audio data
   2. Subject sub-003 session ses-001 missing task soundrecognition
   3. Mixed session structure: 2 subjects have sessions, 1 don't

�📊 SUMMARY: 1 errors, 3 warnings
❌ Dataset validation failed due to errors.
```

## Consistency Checking

The validator performs cross-subject consistency checks to ensure scientific rigor:

- **Modality consistency**: All subjects should have the same modalities (e.g., if one subject has both image and audio data, all should)
- **Task consistency**: All subjects should perform the same tasks within each session
- **Session structure**: Warns if mixing subjects with and without session directories
- **Per-session consistency**: For multi-session studies, ensures each subject has consistent data across sessions

These checks generate **warnings** (not errors) since missing data might be due to technical issues, dropouts, or valid experimental design decisions.

### Exit codes:
- `0`: Dataset is valid
- `1`: Validation errors found

## Test Dataset

The included `test_dataset/` demonstrates:
- ✅ Valid files with proper naming and metadata
- ❌ Invalid naming conventions
- ❌ Missing sidecar files
- ✅ Mixed session/no-session structures

## 📁 Repository Structure

- **`prism-validator-web.py`** - **✨ MAIN ENTRY POINT** - Web interface with NeuroBagel integration
- `schemas/` - JSON schemas for each modality
- `docs/` - Documentation (web interface guide, examples, NeuroBagel integration)
- `tests/` - Test dataset and test scripts
- `src/` - Core validation and utility modules
- `static/` - Web interface assets (CSS, JavaScript, NeuroBagel widget)
- `templates/` - Web interface templates (HTML)
- `archive/` - Legacy scripts

### Additional Files
- `prism-validator.py` - Command-line tool (see footnote below)
- `setup.sh` / `setup-windows.bat` - Installation scripts
- `requirements.txt` - Python dependencies

## 🔬 NeuroBagel Integration (v1.1.0+)

The JSON Editor now includes professional **NeuroBagel annotation tools** for standardizing participant metadata:

### Features:
- **Automatic TSV Parsing**: Loads unique values from `participants.tsv`
- **Smart Categorization**: Separates available columns from suggestions
- **Data Type Detection**: Auto-detects continuous vs. categorical variables
- **Ontology Integration**: Add SNOMED-CT URIs to categorical levels
- **Standardized Export**: Downloads annotated `participants.json` with full BIDS compliance

### Workflow:
1. Upload dataset with `participants.json` and `participants.tsv`
2. Go to JSON Editor → Select "Annotate Participants"
3. Edit column descriptions, units, and categorical levels
4. Add ontology URIs (SNOMED-CT shorthand: `snomed:248153007`)
5. Download annotated file to replace original

See [`docs/NEUROBAGEL_INTEGRATION_STRATEGY.md`](docs/NEUROBAGEL_INTEGRATION_STRATEGY.md) for details.

---

## 📚 Additional Resources

- **[Web Interface Documentation](docs/WEB_INTERFACE.md)** - Detailed UI guide
- **[NeuroBagel Integration](docs/NEUROBAGEL_INTEGRATION_STRATEGY.md)** - Annotation tool usage
- **[Schema Versioning Guide](docs/SCHEMA_VERSIONING_GUIDE.md)** - Multiple schema versions
- **[Examples](docs/examples/)** - Test datasets and example files
- **[FAIR Implementation](docs/FAIR_IMPLEMENTATION.md)** - FAIR data principles

---

## 🔮 Future Enhancements

1. **Additional modalities**: Add schemas for EEG, eye-tracking, and behavioral data
2. **Cross-file validation**: Validate stimulus-response timing relationships
3. **BIDS compatibility**: Ensure full compatibility with official BIDS standard
4. **Batch processing**: Support for validating multiple datasets via web UI
5. **Export formats**: BIDS package export, DataLad integration

## Installation

### ⚡ Quick Setup (Recommended)

**macOS/Linux:**
```bash
git clone https://github.com/MRI-Lab-Graz/prism-validator.git
cd prism-validator
bash setup.sh
python prism-validator-web.py
```

**Windows:**
```cmd
git clone https://github.com/MRI-Lab-Graz/prism-validator.git
cd prism-validator
scripts\setup-windows.bat
python prism-validator-web.py
```

The web interface opens automatically! 🌐

### Manual Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run web interface
python prism-validator-web.py
```

---

## 📖 Usage Guide

### 🌐 Web Interface (Primary - Recommended for All Users)

Simply run:
```bash
python prism-validator-web.py
```

The interface opens at `http://localhost:5001` with three main sections:

#### 1. **Dataset Validation** (Home Tab)
- Drag & drop your dataset folder or ZIP file
- Select schema version (stable/v0.1)
- Get instant validation results with visual charts

#### 2. **JSON Editor** (JSON Editor Tab)
- Edit dataset_description.json and other metadata
- Create new metadata files
- **NeuroBagel Annotation Tool** (if participants.json exists):
  - Load your dataset with participants.json
  - Select "Annotate Participants" 
  - Annotation widget loads your participants.tsv data
  - Edit descriptions, units, and categorical levels
  - Add SNOMED-CT URIs for ontology standardization
  - Download annotated participants.json

#### 3. **Home Page**
- Introduction and quick links
- Feature overview
- Getting started guide

**Features:**
- ✅ All processing happens locally (no data leaves your machine)
- ✅ Real-time validation feedback
- ✅ Support for folder and ZIP uploads
- ✅ Interactive metadata editing
- ✅ Professional annotation with NeuroBagel

See [`docs/WEB_INTERFACE.md`](docs/WEB_INTERFACE.md) for detailed instructions.

---

### 📝 Command-Line Interface (Advanced/Automation)

For automation and scripting, use the CLI:

```bash
# Activate virtual environment first
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Basic validation (uses stable schema)
python prism-validator.py /path/to/dataset

# Validate with specific schema version
python prism-validator.py /path/to/dataset --schema-version v0.1

# List available schema versions
python prism-validator.py --list-versions

# Verbose output
python prism-validator.py /path/to/dataset -v

# Show help
python prism-validator.py --help
```

**Note:** This is primarily for automation and batch processing. The web interface is recommended for interactive use.

#### Schema Versions

Available schema versions:
- **`stable`** (default) - Current recommended version
- **`v0.1`** - Version 0.1

See [`docs/SCHEMA_VERSIONING_GUIDE.md`](docs/SCHEMA_VERSIONING_GUIDE.md) for details.

## Dependencies

- Python 3.6+
- `jsonschema` - For JSON schema validation
- `flask` - Web interface framework
- `requests` - HTTP client for NeuroBagel API

Optional (for dummy file generation):
- `Pillow` - For creating test images
- `numpy` - For generating test data

---

## 📝 Footnote: Command-Line Tool

While the **web interface is the primary and recommended method** for using Prism-Validator, a command-line interface is also available for automation and batch processing.

**Command-line tool usage:**
```bash
python prism-validator.py /path/to/dataset [--schema-version VERSION] [-v]
```

This is useful for:
- CI/CD pipelines and automated testing
- Batch processing multiple datasets
- Scripting and automation workflows
- Integration with other tools

For most users and interactive validation, please use the web interface instead.

---

## 💡 License & Attribution

See LICENSE file for details.

For questions or contributions, visit the [GitHub repository](https://github.com/MRI-Lab-Graz/prism-validator).
