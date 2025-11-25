# PRISM Survey JSON Reference

Purpose: This document enumerates every key used (or recommended) in PRISM survey sidecar JSON files, their types, whether they are mandatory, allowed values, examples, and guidance for use. It is intended to be a human-readable reference (an HTML site can be generated from this markdown later).

Scope: Matches `schemas/stable/survey.schema.json` plus a few recommended technical fields (such as `ResponseType`) that appear in practice and in this repository's demo datasets.

---

**Top-level structure**
- **Type**: object
- **Required**: `Technical`, `Study`, `Metadata`
- **Additional properties**: each additional property is expected to be a survey item (question) object; see "Question / Item-level fields" below.

## 1) `Technical` (object)
- **Mandatory**: yes
- **Type**: object
- **Purpose**: describes the file format, platform and who answered the survey.

Sub-keys:
- **`StimulusType`**: (string) — Mandatory. Allowed value: `"Questionnaire"`.
  - Example: `"StimulusType": "Questionnaire"`
- **`FileFormat`**: (string) — Mandatory. Allowed value: `"tsv"` (PRISM stores tabular survey responses in TSV files).
  - Example: `"FileFormat": "tsv"`
- **`SoftwarePlatform`**: (string) — Mandatory. Free-text (e.g., `"LimeSurvey"`, `"RedCap"`, `"Qualtrics"`). Provide the platform and (optionally) version.
  - Example: `"SoftwarePlatform": "LimeSurvey 5.4"`
- **`Language`**: (string) — Mandatory. IETF language tag recommended (e.g., `en`, `en-US`, `de-AT`). The schema enforces a simple pattern like `xx` or `xx-XX`.
  - Example: `"Language": "en"`
- **`Respondent`**: (string) — Mandatory. Who provided the answers. Allowed/common values: `"self"`, `"clinician"`, `"parent"`, `"teacher"`, `"other"`.
  - Example: `"Respondent": "self"`

- **`ResponseType`**: (array[string]) — Optional (recommended). Not required by the current `survey.schema.json` but often useful to describe how responses were collected. Typical options and guidance below:
  - Recommended enumeration (examples): `"button"` (button click UI), `"keypress"` (keyboard press), `"touchscreen"`, `"paper-pencil"` (pen-and-paper), `"online"` (web-form generic), `"voice"`, `"pen_and_paper"`, `"other"`.
  - Use-cases:
    - Use `"button"` when the frontend presented explicitly clickable buttons (common for Likert scales in web UI).
    - Use `"paper-pencil"` or `"pen_and_paper"` for scanned / manually-entered questionnaires.
    - Use `"online"` as a generic tag when the platform is web-based and the precise input method is not needed.
  - Example: `"ResponseType": ["button"]`

Notes:
- Keep `Technical` concise but accurate — it helps downstream users interpret values and processing scripts.

## 2) `Study` (object)
- **Mandatory**: yes
- **Type**: object
- **Purpose**: identifies the instrument used and its canonical metadata.

Sub-keys:
- **`TaskName`**: (string) — Mandatory. Short identifier used in filenames and task-level indexing. Pattern: alphanumeric (no spaces), e.g., `bdi`, `ads`, `psqi`.
  - Example: `"TaskName": "bdi"`
- **`OriginalName`**: (string) — Mandatory. Human-readable canonical name of the instrument.
  - Example: `"OriginalName": "Beck Depression Inventory"`
- **`Version`**: (string) — Optional. Instrument version (if applicable).
  - Example: `"Version": "II"`
- **`Citation`**: (string) — Optional. DOI, URL or bibliographic citation.
  - Example: `"Citation": "Beck et al. 1961; DOI:10.xxxx/yyyy"`

## 3) `Metadata` (object)
- **Mandatory**: yes
- **Type**: object
- **Purpose**: administrative metadata about the sidecar itself.

Sub-keys:
- **`SchemaVersion`**: (string) — Mandatory. Semantic version of the schema used (e.g., `"1.0.0"`).
- **`CreationDate`**: (string, date) — Mandatory. Date (YYYY-MM-DD) when the sidecar was produced.
- **`Creator`**: (string) — Optional. Person or system that generated the sidecar.

Example:
```
"Metadata": {
  "SchemaVersion": "1.0.0",
  "CreationDate": "2025-11-24",
  "Creator": "prism limesurvey converter"
}
```

## 4) Question / Item-level fields (applies to any additional top-level property)
Any top-level property not named `Technical`, `Study`, or `Metadata` is interpreted as a question/item definition. The schema enforces that these are objects and require at minimum a `Description` string. Recommended fields:

- **`Description`** (string) — Mandatory for each item. The exact question text presented to the participant.
  - Example: `"Description": "I feel sad"`
- **`Levels`** (object) — Optional. Maps numeric or coded response values to their labels. Keys may be numbers or strings.
  - Example:
    ```json
    "Levels": { "0": "Not at all", "1": "Several days", "2": "More than half the days", "3": "Nearly every day" }
    ```
- **`Units`** (string) — Optional. If the item has units (rare for surveys), e.g., `"seconds"`.
- **`TermURL`** (string, uri) — Optional. Link to a definition or canonical term (for ontologies or definitions).
- **`Relevance`** (string) — Optional. Logic expression used to show or hide this item (e.g., `Q01 == 1` or `age >= 18`). Implementation depends on the target platform; when converting to LimeSurvey this may be turned into the platform's relevance expression.

Notes on question IDs / keys:
- The top-level property name for a question can be any valid JSON key, but in practice use a short stable ID (e.g., `Q01`, `Q1`, `q_bdi_1`). Keep it ASCII and avoid spaces.

## 5) Folder + filename conventions
- **Folder**: place survey data under `sub-<id>[/ses-<id>]/survey/`. Reserve `beh/` for other behavioral tasks (reaction-time, derivatives, etc.).
- **Dataset-level sidecar**: `survey-<name>.json` (inside dataset root or `surveys/`).
- **Per-subject TSV**: `sub-<label>[_ses-<label>]_survey-<name>.tsv` stored inside each `survey/` folder.

- Example layout:

```
PK01/rawdata/
  survey-ads.json
  survey-psqi.json
  sub-1291003/
    ses-1/
      survey/
        sub-1291003_ses-1_survey-ads.tsv
        sub-1291003_ses-1_survey-psqi.tsv
      beh/
        sub-1291003_ses-1_task-ecg_beh.tsv
```

- Rationale: `survey-<name>` makes the modality explicit, keeps folders semantically clean, and still passes BIDS-style validation. If you must stay compatible with legacy data, the validator continues to accept `_task-<name>_beh`, but migrating to the pure `survey` layout is preferred.

### Single-root sidecar recommendation

- Recommendation: When the same questionnaire sidecar content applies to every subject (identical `Technical`, `Study`, questions and question metadata), keep a single canonical sidecar at the dataset root (or in a dedicated `surveys/` folder) instead of copying identical files per subject.

- Advantages:
  - Single source of truth: avoid drift when updating question text or levels.
  - Smaller repository size: fewer duplicate files.
  - Easier maintenance and clearer provenance.

- Example canonical placement options:
  - Root-level: `survey-bdi.json`
  - Under `surveys/`: `surveys/survey-bdi.json`

- Example file naming when using a root-level sidecar and per-subject TSV responses:
  - Sidecar: `survey-bdi.json`
  - Subject responses: `sub-001_ses-1_survey-bdi.tsv`, `sub-002_ses-1_survey-bdi.tsv`, etc.

- How the validator typically resolves sidecars:
  - Many validators look for an exact sidecar adjacent to the data file (same folder) and then fall back to dataset-level or modality-level sidecars. Check your validator's resolution order — if the validator supports dataset-level sidecars, prefer the root-level approach.

- Quick consolidation commands (POSIX / macOS zsh):

  1) Create a single root sidecar by copying one existing per-subject JSON (verify content first):

```bash
cp prism_demo/sub-001/survey/sub-001_survey-bdi.json prism_demo/survey-bdi.json
```

  2) Rename/move per-subject TSVs from legacy `beh/` folders:

```bash
for beh_dir in prism_demo/sub-*/ses-*/beh; do
  survey_dir="${beh_dir%/beh}/survey"
  mkdir -p "$survey_dir"
  for file in "$beh_dir"/*_survey-*_beh.tsv; do
    [ -e "$file" ] || continue
    base=$(basename "$file" _beh.tsv)
    mv "$file" "$survey_dir/${base##*/}.tsv"
  done
done
```

  3) Remove or archive per-subject JSON sidecars (if you confirmed dataset-level resolution works):

```bash
find prism_demo -name "sub-*_survey-*.json" -type f -delete
```

Notes:
- Before removing per-subject JSON files, ensure your validator supports dataset-level sidecars or adjust the validator configuration. If unsure, keep backups (`.bak`) as shown.

## 6) Examples

Minimal BDI sidecar (compact):

```json
{
  "Technical": {
    "StimulusType": "Questionnaire",
    "FileFormat": "tsv",
    "SoftwarePlatform": "LimeSurvey 5.4",
    "Language": "en",
    "Respondent": "self",
    "ResponseType": ["button"]
  },
  "Study": {
    "TaskName": "bdi",
    "OriginalName": "Beck Depression Inventory"
  },
  "Metadata": {
    "SchemaVersion": "1.0.0",
    "CreationDate": "2025-11-24",
    "Creator": "limesurvey_to_prism.py"
  },
  "Q01": {
    "Description": "I feel sad",
    "Levels": {"0": "Not at all", "1": "Several days", "2": "More than half the days", "3": "Nearly every day"}
  }
}
```

## 7) Guidance & best practices
- Always include `Description` for each question — this is the minimum that makes a sidecar useful.
- Prefer standardized `Levels` so tools can map numeric values to text labels reliably.
- Include `ResponseType` when you convert from a platform that uses different input mechanisms; it helps downstream viewers and scripts decide how to display items.
- Use stable `TaskName` values; they are used in filenames and aggregator tools.
- Keep `Language` and `SoftwarePlatform` accurate — essential for reuse and metadata-driven audits.

## 8) Handling licensed questionnaires
- Some instruments (e.g., BDI, BIS/BAS) are copyrighted. You may collect data internally but cannot redistribute the exact question text. Use `scripts/redact_sidecar.py` to generate a sanitized sidecar for public releases:

```bash
python3 scripts/redact_sidecar.py \
  prism_demo/survey-bdi.json \
  prism_demo/survey-bdi.public.json \
  --fields Description Levels --placeholder "[CONTACT PI]" --drop-levels
```

- Flags:
  - `--fields Description Levels` replaces both the prompt and label lookups.
  - `--hash` keeps a SHA256 digest instead of a placeholder so you can verify provenance privately.
  - `--keep-empty` retains items even if every sensitive field is removed (default drops blank entries).

- Store the fully detailed sidecar internally and publish the redacted copy alongside TSVs. Downstream users can still interpret column names and scoring logic without seeing protected text.

## 9) Extensibility
- The PRISM sidecar allows extra keys at top-level for items and at item-level for more complex metadata (e.g., psychometric properties). When adding new fields, prefer names that are self-explanatory and document them here.

---

If you want, I can:
- Convert this markdown into an HTML reference page and add navigation into the docs site.
- Extend the schema to formally include `ResponseType` and a canonical enum of allowed values (so the validator enforces it).

Please tell me if you'd like any additional keys documented or if you prefer different canonical values for `ResponseType`.
