"""
Core validation logic for prism-validator
"""

import os
import re
import json
from jsonschema import validate, ValidationError
from cross_platform import (
    normalize_path,
    safe_path_join,
    CrossPlatformFile,
    validate_filename_cross_platform,
)

# Modality patterns
MODALITY_PATTERNS = {
    "movie": r".+\.mp4$",
    "image": r".+\.(png|jpg|jpeg|tiff)$",
    "eyetracking": r".+\.(tsv|edf)$",
    "audio": r".+\.(wav|mp3)$",
    "survey": r".+\.tsv$",
    "physiological": r".+\.(edf|bdf|txt|csv)$",
    # MRI submodalities
    "anat": r".+_(T1w|T2w|T2star|FLAIR|PD|PDw|T1map|T2map)\.nii(\.gz)?$",
    "func": r".+_bold\.nii(\.gz)?$",
    "fmap": r".+_(magnitude1|magnitude2|phasediff|fieldmap|epi)\.nii(\.gz)?$",
    "dwi": r".+_dwi\.nii(\.gz)?$",
}

# BIDS naming patterns
BIDS_REGEX = re.compile(
    r"^sub-[a-zA-Z0-9]+"
    r"(_ses-[a-zA-Z0-9]+)?"
    r"(_(task|survey)-[a-zA-Z0-9]+)?"
    r"(_run-[0-9]+)?"
)

MRI_SUFFIX_REGEX = re.compile(
    r"_(T1w|T2w|T2star|FLAIR|PD|PDw|T1map|T2map|bold|dwi|magnitude1|magnitude2|phasediff|fieldmap|epi)$"
)

# File extensions that need special handling
COMPOUND_EXTS = (".nii.gz", ".tsv.gz", ".edf.gz")


def split_compound_ext(filename):
    """Return (stem, ext) and handle compound extensions like .nii.gz."""
    if any(filename.endswith(ext) for ext in COMPOUND_EXTS):
        for ext in COMPOUND_EXTS:
            if filename.endswith(ext):
                stem = filename[: -len(ext)]
                return stem, ext
    base, ext = os.path.splitext(filename)
    return base, ext


def derive_sidecar_path(file_path):
    """Derive the JSON sidecar path for a data file."""
    file_path = normalize_path(file_path)
    dirname = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    stem, _ext = split_compound_ext(fname)
    return safe_path_join(dirname, f"{stem}.json")


def _extract_entity_value(stem, key):
    match = re.search(rf"_{key}-([a-zA-Z0-9]+)", stem)
    if match:
        return match.group(1)
    return None


def resolve_sidecar_path(file_path, root_dir):
    """Return best-matching sidecar path, supporting dataset-level survey sidecars."""
    candidate = derive_sidecar_path(file_path)
    if os.path.exists(candidate):
        return candidate

    stem, _ext = split_compound_ext(os.path.basename(file_path))
    suffix = ""
    if "_" in stem:
        suffix = stem.split("_")[-1]

    survey_value = _extract_entity_value(stem, "survey")
    task_value = _extract_entity_value(stem, "task")

    label_candidates = []
    if survey_value:
        label_candidates.append(("survey", survey_value))
    if task_value:
        label_candidates.append(("task", task_value))
        if not survey_value:
            label_candidates.append(("survey", task_value))

    search_dirs = [root_dir, safe_path_join(root_dir, "surveys")]

    for prefix, value in label_candidates:
        base_name = f"{prefix}-{value}"
        suffix_part = f"_{suffix}" if suffix and suffix != base_name else ""
        file_name = f"{base_name}{suffix_part}.json"
        for directory in search_dirs:
            if not directory:
                continue
            dataset_candidate = safe_path_join(directory, file_name)
            if os.path.exists(dataset_candidate):
                return dataset_candidate

    return candidate


class DatasetValidator:
    """Main dataset validation class"""

    def __init__(self, schemas=None):
        self.schemas = schemas or {}

    def validate_filename(self, filename, modality):
        """Validate filename against BIDS conventions and modality patterns"""
        issues = []

        # Cross-platform filename validation
        platform_issues = validate_filename_cross_platform(filename)
        for issue in platform_issues:
            issues.append(("WARNING", issue))

        base, ext = split_compound_ext(filename)
        pattern = re.compile(MODALITY_PATTERNS.get(modality, r".*"))

        # Check BIDS naming
        if not BIDS_REGEX.match(base):
            issues.append(("ERROR", f"Invalid BIDS filename format: {filename}"))

        # Check modality pattern
        if not pattern.match(filename):
            issues.append(
                (
                    "WARNING",
                    f"Filename doesn't match expected pattern for {modality}: {filename}",
                )
            )

        # Check MRI-specific patterns
        if modality in ("anat", "func", "fmap", "dwi"):
            if ext in (".nii", ".nii.gz") and not MRI_SUFFIX_REGEX.search(base):
                issues.append(
                    ("ERROR", f"Invalid MRI suffix for {modality}: {filename}")
                )

        return issues

    def validate_sidecar(self, file_path, modality, root_dir):
        """Validate JSON sidecar against schema"""
        sidecar_path = resolve_sidecar_path(file_path, root_dir)
        issues = []

        if not os.path.exists(sidecar_path):
            return [("ERROR", f"Missing sidecar for {normalize_path(file_path)}")]

        try:
            # Use cross-platform file reading
            content = CrossPlatformFile.read_text(sidecar_path)
            sidecar_data = json.loads(content)

            # Validate against schema if available
            schema = self.schemas.get(modality)
            if schema:
                validate(instance=sidecar_data, schema=schema)

        except ValidationError as e:
            issues.append(
                ("ERROR", f"{normalize_path(sidecar_path)} schema error: {e.message}")
            )
        except json.JSONDecodeError as e:
            issues.append(
                ("ERROR", f"{normalize_path(sidecar_path)} is not valid JSON: {e}")
            )
        except Exception as e:
            issues.append(
                ("ERROR", f"Error processing {normalize_path(sidecar_path)}: {e}")
            )

        return issues
