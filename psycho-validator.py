import os
import re
import json
from jsonschema import validate, ValidationError

# ----------------------------
# Regex for BIDS-style filenames
# ----------------------------
BIDS_REGEX = re.compile(
    r"^sub-[a-zA-Z0-9]+"
    r"(_ses-[a-zA-Z0-9]+)?"
    r"_task-[a-zA-Z0-9]+"
    r"(_run-[0-9]+)?"
)

# ----------------------------
# Modality definitions
# ----------------------------
MODALITY_PATTERNS = {
    "movies": r".+\.mp4$",
    "images": r".+\.(png|jpg|jpeg|tiff)$",
    "eye-tracking": r".+\.(tsv|edf)$",
    "eeg": r".+\.(edf|bdf|eeg)$",
    "audio": r".+\.(wav|mp3)$",
    "behavior": r".+\.tsv$"
}

# ----------------------------
# Load modality schemas
# ----------------------------
def load_schema(name):
    path = os.path.join("schemas", f"{name}-bids.schema.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

SCHEMAS = {m: load_schema(m) for m in MODALITY_PATTERNS}

# ----------------------------
# Helper: validate sidecar JSON
# ----------------------------
def validate_sidecar(file_path, schema):
    sidecar = file_path.replace(os.path.splitext(file_path)[1], ".json")
    issues = []
    if not os.path.exists(sidecar):
        issues.append(("ERROR", f"Missing sidecar for {file_path}"))
    else:
        try:
            with open(sidecar) as f:
                meta = json.load(f)
            if schema:
                validate(instance=meta, schema=schema)
        except ValidationError as e:
            issues.append(("ERROR", f"{sidecar} schema error: {e.message}"))
        except json.JSONDecodeError:
            issues.append(("ERROR", f"{sidecar} is not valid JSON"))
    return issues

# ----------------------------
# Main validator
# ----------------------------
def validate_dataset(root_dir):
    issues = []

    # 1. Dataset-level checks
    if not os.path.exists(os.path.join(root_dir, "dataset_description.json")):
        issues.append(("ERROR", "Missing dataset_description.json"))
    if not os.path.exists(os.path.join(root_dir, "participants.tsv")):
        issues.append(("WARNING", "Missing participants.tsv"))

    # 2. Walk through subfolders
    for dirpath, _, filenames in os.walk(root_dir):
        modality = os.path.basename(dirpath)
        if modality in MODALITY_PATTERNS:
            pattern = re.compile(MODALITY_PATTERNS[modality])
            schema = SCHEMAS.get(modality)
            for fname in filenames:
                if pattern.match(fname):
                    # Check naming convention
                    base, ext = os.path.splitext(fname)
                    if not BIDS_REGEX.match(base):
                        issues.append(("ERROR", f"Invalid filename: {fname}"))
                    # Check sidecar schema
                    file_path = os.path.join(dirpath, fname)
                    issues += validate_sidecar(file_path, schema)

    return issues

# ----------------------------
# CLI entry point
# ----------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Psycho-Validator (BIDS-inspired)")
    parser.add_argument("dataset", help="Path to dataset root")
    args = parser.parse_args()

    problems = validate_dataset(args.dataset)
    if not problems:
        print("✅ Dataset is valid!")
    else:
        for level, msg in problems:
            print(f"[{level}] {msg}")
