# PRISM demo structure (temporary for live presentation)

This folder contains a **minimal PRISM-style demo dataset** to show the idea of a hierarchical psychological data structure, inspired by BIDS but focused on tasks and modalities.

Top-level files
- `prism_description.json` — placeholder for dataset-level metadata and PRISM version.
- `participants.tsv` — placeholder list of participants.
- `tasks.tsv` — placeholder overview of tasks used in the dataset.
- `schemas/` — JSON Schemas used to validate the dataset structure and metadata.

Subjects and sessions
- `sub-001/ses-01/`
  - `task/` — trial-level behavioural data for a task (e.g. Stroop).
  - `eeg/` — EEG recording files and sidecar metadata.
  - `eye/` — eye-tracking data.
  - `questionnaires/` — questionnaire responses (e.g. BDI).
  - `metadata/` — session-level metadata.
- `sub-002/ses-01/` — same structure as `sub-001/ses-01/` with different IDs.

All files here are **dummy placeholders** with correct naming only. Replace them with real data and metadata when you build an actual PRISM dataset.
