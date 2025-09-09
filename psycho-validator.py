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
    "movie": r".+\.mp4$",
    "image": r".+\.(png|jpg|jpeg|tiff)$",
    "eyetracking": r".+\.(tsv|edf)$",
    "eeg": r".+\.(edf|bdf|eeg)$",
    "audio": r".+\.(wav|mp3)$",
    "behavior": r".+\.tsv$"
}

# ----------------------------
# Load modality schemas
# ----------------------------
def load_schema(name):
    schema_path = os.path.join("schemas", f"{name}.schema.json")
    if os.path.exists(schema_path):
        try:
            with open(schema_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load schema {schema_path}: {e}")
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
    dataset_desc_path = os.path.join(root_dir, "dataset_description.json")
    if not os.path.exists(dataset_desc_path):
        issues.append(("ERROR", "Missing dataset_description.json"))
    
    participants_path = os.path.join(root_dir, "participants.tsv")
    if not os.path.exists(participants_path):
        issues.append(("WARNING", "Missing participants.tsv"))

    # 2. Walk through subject directories
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item.startswith("sub-"):
            # This is a subject directory
            issues += validate_subject(item_path, item)

    return issues

def validate_subject(subject_dir, subject_id):
    """Validate a single subject directory"""
    issues = []
    
    for item in os.listdir(subject_dir):
        item_path = os.path.join(subject_dir, item)
        if os.path.isdir(item_path):
            if item.startswith("ses-"):
                # Session directory
                issues += validate_session(item_path, subject_id, item)
            elif item in MODALITY_PATTERNS:
                # Direct modality directory (no sessions)
                issues += validate_modality_dir(item_path, subject_id, None, item)
    
    return issues

def validate_session(session_dir, subject_id, session_id):
    """Validate a single session directory"""
    issues = []
    
    for item in os.listdir(session_dir):
        item_path = os.path.join(session_dir, item)
        if os.path.isdir(item_path) and item in MODALITY_PATTERNS:
            issues += validate_modality_dir(item_path, subject_id, session_id, item)
    
    return issues

def validate_modality_dir(modality_dir, subject_id, session_id, modality):
    """Validate files in a modality directory"""
    issues = []
    pattern = re.compile(MODALITY_PATTERNS[modality])
    schema = SCHEMAS.get(modality)
    
    for fname in os.listdir(modality_dir):
        file_path = os.path.join(modality_dir, fname)
        if os.path.isfile(file_path) and pattern.match(fname):
            # Check naming convention
            base, ext = os.path.splitext(fname)
            if not BIDS_REGEX.match(base):
                issues.append(("ERROR", f"Invalid filename: {fname} in {modality_dir}"))
            
            # Validate expected subject/session in filename
            if subject_id not in fname:
                issues.append(("ERROR", f"Filename {fname} doesn't contain subject ID {subject_id}"))
            
            if session_id and session_id not in fname:
                issues.append(("ERROR", f"Filename {fname} doesn't contain session ID {session_id}"))
            
            # Check sidecar schema
            issues += validate_sidecar(file_path, schema)
    
    return issues

# ----------------------------
# CLI entry point
# ----------------------------
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Psycho-Validator (BIDS-inspired)")
    parser.add_argument("dataset", help="Path to dataset root")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Show detailed validation information")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"❌ Dataset directory not found: {args.dataset}")
        sys.exit(1)

    print(f"🔍 Validating dataset: {args.dataset}")
    if args.verbose:
        print(f"📁 Scanning for modalities: {list(MODALITY_PATTERNS.keys())}")
        print(f"📋 Available schemas: {[k for k, v in SCHEMAS.items() if v is not None]}")
    
    problems = validate_dataset(args.dataset)

    if not problems:
        print("✅ Dataset is valid!")
    else:
        error_count = sum(1 for level, _ in problems if level == "ERROR")
        warning_count = sum(1 for level, _ in problems if level == "WARNING")
        
        print(f"\n❌ Found {error_count} errors and {warning_count} warnings:")
        for level, msg in problems:
            emoji = "🔴" if level == "ERROR" else "🟡"
            print(f"  {emoji} [{level}] {msg}")
        
        if error_count > 0:
            sys.exit(1)
