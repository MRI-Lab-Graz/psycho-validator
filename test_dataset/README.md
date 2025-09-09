# Test Dataset for Psycho-Validator

This is a dummy test dataset designed to validate the psycho-validator tool. It follows a BIDS-inspired structure for psychophysiology experiments.

## Dataset Structure

```
test_dataset/
├── dataset_description.json     # Required BIDS dataset description
├── participants.tsv            # Participant information
├── sub-001/                    # Subject with sessions
│   └── ses-001/
│       ├── image/
│       │   ├── sub-001_ses-001_task-facerecognition_run-01_stim.png
│       │   └── sub-001_ses-001_task-facerecognition_run-01_stim.json
│       └── audio/
│           ├── sub-001_ses-001_task-soundrecognition_run-01_stim.wav
│           └── sub-001_ses-001_task-soundrecognition_run-01_stim.json
├── sub-002/                    # Subject without sessions
│   └── movie/
│       ├── sub-002_task-moviewatch_run-01_stim.mp4
│       └── sub-002_task-moviewatch_run-01_stim.json
└── sub-003/                    # Subject with validation errors
    └── ses-001/
        └── image/
            ├── sub-003_ses-001_task-facerecognition_invalid-naming.jpg  # Invalid naming
            ├── sub-003_ses-001_task-facerecognition_run-02_stim.jpg     # Valid file
            └── sub-003_ses-001_task-facerecognition_run-02_stim.json    # Missing PresentedWith field
```

## Modalities Included

- **image**: Static images (PNG, JPG, TIFF)
- **audio**: Audio stimuli (WAV, MP3)
- **movie**: Video stimuli (MP4)

## Test Cases

The dataset includes:

1. **Valid files**: Properly named with complete sidecar metadata
2. **Invalid naming**: Files that don't follow BIDS naming conventions
3. **Missing metadata**: JSON sidecars with missing required fields
4. **Mixed structure**: Some subjects with sessions, others without

## Running the Validator

To test the validator on this dataset:

```bash
python psycho-validator.py test_dataset/
```

Expected output should show validation errors for the deliberately malformed files.
