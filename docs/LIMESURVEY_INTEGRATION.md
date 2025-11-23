# LimeSurvey Integration Guide

This guide explains how to prepare and convert LimeSurvey questionnaires for use with the Prism-Validator pipeline.

## Overview

To ensure a smooth conversion from LimeSurvey to the Prism/BIDS structure, you need to:
1.  **Prepare** your LimeSurvey questionnaire with consistent variable naming.
2.  **Export** the survey structure (.lss) and data (.csv).
3.  **Convert** the structure to a Prism JSON sidecar.
4.  **Format** the data as a BIDS-compatible TSV file.

## 1. Preparation in LimeSurvey

When creating your survey in LimeSurvey, follow these conventions to make conversion easier:

### Variable Naming (Codes)
*   **Question Codes**: Use short, alphanumeric codes (e.g., `ADS01`, `BDI05`, `AGE`). These will become your column headers.
*   **Subquestion Codes**: For array questions, use simple suffixes (e.g., `SQ001`, `01`). LimeSurvey automatically combines these (e.g., `ADS_SQ001`).
*   **Avoid Special Characters**: Do not use spaces or special characters in codes.

### Answer Options
*   **Codes**: Use numeric codes for answer options (e.g., `0`, `1`, `2`, `3`) rather than text (e.g., `A1`, `A2`). This makes analysis easier.
*   **Text**: The text label (e.g., "Strongly Agree") will be automatically extracted into the JSON sidecar's `Levels` field.

## 2. Exporting from LimeSurvey

### Structure Export (for JSON Sidecar)
1.  Go to **Display/Export** > **Survey structure (.lss)**.
2.  Click **Export**.
3.  Save the `.lss` file (e.g., `my_survey.lss`).

### Data Export (for Data Files)
1.  Go to **Responses** > **Export** > **Export results**.
2.  **Format**: Select `CSV` or `Microsoft Excel`.
3.  **General**:
    *   **Heading format**: `Question code` (Crucial! Do not use full question text).
    *   **Response format**: `Answer codes` (Recommended for analysis) or `Long answer text`.
4.  Export and save.

## 3. Converting to Prism JSON

We provide a script to automatically generate the JSON sidecar from your `.lss` file.

```bash
# Basic usage
python scripts/limesurvey_to_prism.py my_survey.lss

# Specify output filename
python scripts/limesurvey_to_prism.py my_survey.lss task-mysurvey_beh.json
```

This script will:
*   Extract all questions and subquestions.
*   Map Question Codes to JSON keys.
*   Map Question Text to `Description`.
*   Map Answer Options to `Levels`.
*   Add required Prism metadata (`Technical`, `Study`, etc.).

## 4. Finalizing the Dataset

1.  **Rename Data File**: Convert your exported CSV/Excel to TSV and rename it to BIDS format:
    *   `sub-<id>_task-<name>_beh.tsv`
    *   Example: `sub-001_task-mysurvey_beh.tsv`
2.  **Place JSON Sidecar**: Place the generated JSON file alongside the data file (or in the root directory if it applies to all subjects).
    *   `task-mysurvey_beh.json`
3.  **Validate**: Run the Prism-Validator to ensure everything is correct.

## 5. Reverse Engineering: JSON to LimeSurvey

If you prefer to define your questionnaires in JSON first (or have existing BIDS sidecars), you can generate a LimeSurvey structure file (`.lss`) from them.

```bash
python scripts/prism_to_limesurvey.py task-bdi_beh.json bdi.lss
```

**Features:**
*   Converts JSON keys to Question Codes.
*   Converts `Description` to Question Text.
*   Converts `Levels` to "List (Radio)" answer options.
*   Questions without `Levels` become "Long Free Text".

**Usage:**
1.  Run the script to generate the `.lss` file.
2.  In LimeSurvey, go to **Create Survey** > **Import**.
3.  Select the generated `.lss` file.

## Example Workflow

1.  You create a survey "Depression Scale" with code `ADS`.
2.  Question 1 code: `Q01`, Answer options: `0=Rarely`, `1=Sometimes`.
3.  Export `ads.lss`.
4.  Run: `python scripts/limesurvey_to_prism.py ads.lss task-ads_beh.json`.
5.  The generated JSON will look like:

```json
{
  "Q01": {
    "Description": "I felt depressed.",
    "Levels": {
      "0": "Rarely",
      "1": "Sometimes"
    }
  },
  "Technical": { ... }
}
```
