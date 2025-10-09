"""
Runner module exposing the canonical validate_dataset function.
This is a refactor target so other tools (web UI) can import the function
without executing the top-level CLI script.
"""

import os
import sys

from schema_manager import load_all_schemas
from validator import DatasetValidator, MODALITY_PATTERNS
from stats import DatasetStats
from system_files import filter_system_files

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def validate_dataset(root_dir, verbose=False, schema_version=None):
    """Main dataset validation function (refactored from psycho-validator.py)

    Args:
        root_dir: Root directory of the dataset
        verbose: Enable verbose output
        schema_version: Schema version to use (e.g., 'stable', 'v0.1', '0.1')

    Returns: (issues, stats)
    """
    issues = []
    stats = DatasetStats()

    # Load schemas with specified version
    schema_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")
    schemas = load_all_schemas(schema_dir, version=schema_version)

    if verbose:
        version_tag = schema_version or "stable"
        print(f"📋 Loaded {len(schemas)} schemas (version: {version_tag})")
        print(f"📁 Scanning modalities: {list(MODALITY_PATTERNS.keys())}")

    # Initialize validator
    validator = DatasetValidator(schemas)

    # Check for dataset description
    dataset_desc_path = os.path.join(root_dir, "dataset_description.json")
    if not os.path.exists(dataset_desc_path):
        issues.append(("ERROR", "Missing dataset_description.json"))

    # Walk through subject directories
    all_items = os.listdir(root_dir)
    filtered_items = filter_system_files(all_items)

    if verbose and len(all_items) != len(filtered_items):
        ignored_count = len(all_items) - len(filtered_items)
        print(f"🗑️  Ignored {ignored_count} system files (.DS_Store, Thumbs.db, etc.)")

    for item in filtered_items:
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item.startswith("sub-"):
            subject_issues = _validate_subject(
                item_path, item, validator, stats, root_dir
            )
            issues.extend(subject_issues)

    # Check cross-subject consistency
    consistency_warnings = stats.check_consistency()
    issues.extend(consistency_warnings)

    return issues, stats


def _validate_subject(subject_dir, subject_id, validator, stats, root_dir):
    issues = []

    all_items = os.listdir(subject_dir)
    filtered_items = filter_system_files(all_items)

    for item in filtered_items:
        item_path = os.path.join(subject_dir, item)
        if os.path.isdir(item_path):
            if item.startswith("ses-"):
                issues.extend(
                    _validate_session(
                        item_path, subject_id, item, validator, stats, root_dir
                    )
                )
            elif item in MODALITY_PATTERNS:
                issues.extend(
                    _validate_modality_dir(
                        item_path, subject_id, None, item, validator, stats, root_dir
                    )
                )

    return issues


def _validate_session(session_dir, subject_id, session_id, validator, stats, root_dir):
    issues = []

    all_items = os.listdir(session_dir)
    filtered_items = filter_system_files(all_items)

    for item in filtered_items:
        item_path = os.path.join(session_dir, item)
        if os.path.isdir(item_path) and item in MODALITY_PATTERNS:
            issues.extend(
                _validate_modality_dir(
                    item_path, subject_id, session_id, item, validator, stats, root_dir
                )
            )

    return issues


def _validate_modality_dir(
    modality_dir, subject_id, session_id, modality, validator, stats, root_dir
):
    issues = []

    all_files = os.listdir(modality_dir)
    filtered_files = filter_system_files(all_files)

    for fname in filtered_files:
        file_path = os.path.join(modality_dir, fname)
        if os.path.isfile(file_path):
            # Extract task from filename
            task = None
            if "_task-" in fname:
                import re

                task_match = re.search(r"_task-([A-Za-z0-9]+)(?:_|$)", fname)
                if task_match:
                    task = task_match.group(1)

            # Add to stats
            stats.add_file(subject_id, session_id, modality, task, fname)

            # Validate filename
            filename_issues = validator.validate_filename(fname, modality)
            issues.extend(filename_issues)

            # Validate sidecar if not JSON file itself
            if not fname.endswith(".json"):
                sidecar_issues = validator.validate_sidecar(
                    file_path, modality, root_dir
                )
                issues.extend(sidecar_issues)

    return issues
