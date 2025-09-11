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
    "behavior": r".+\.tsv$",
    "physiological": r".+\.(edf|bdf|txt|csv)$"
}

# ----------------------------
# Schema Versioning System
# ----------------------------
def parse_version(version_string):
    """Parse semantic version string to tuple of integers"""
    try:
        return tuple(map(int, version_string.split('.')))
    except:
        return (0, 0, 0)

def is_compatible_version(required_version, provided_version):
    """Check if provided version is compatible with required version"""
    req_major, req_minor, req_patch = parse_version(required_version)
    prov_major, prov_minor, prov_patch = parse_version(provided_version)
    
    # Same major version is required for compatibility
    if req_major != prov_major:
        return False
    
    # Minor version can be higher (backward compatible)
    if prov_minor < req_minor:
        return False
        
    # Patch version can be different
    return True

def load_schema(name):
    """Load schema with version information"""
    schema_path = os.path.join("schemas", f"{name}.schema.json")
    if os.path.exists(schema_path):
        try:
            with open(schema_path) as f:
                schema = json.load(f)
            
            # Add schema metadata for versioning
            schema_version = schema.get('version', '1.0.0')
            schema['_validator_info'] = {
                'schema_version': schema_version,
                'modality': name,
                'loaded_at': json.dumps({"timestamp": "runtime"})
            }
            return schema
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load schema {schema_path}: {e}")
    return None

def validate_schema_version(metadata, schema):
    """Validate that metadata schema version is compatible with loaded schema"""
    issues = []
    
    if not schema or '_validator_info' not in schema:
        return issues
    
    schema_version = schema['_validator_info']['schema_version']
    
    # Check if metadata specifies a schema version
    metadata_version = None
    if 'Metadata' in metadata and 'SchemaVersion' in metadata['Metadata']:
        metadata_version = metadata['Metadata']['SchemaVersion']
    
    if metadata_version:
        if not is_compatible_version(schema_version, metadata_version):
            issues.append(("WARNING", 
                f"Schema version mismatch: metadata uses v{metadata_version}, "
                f"validator expects v{schema_version}. Consider upgrading metadata."))
    else:
        issues.append(("INFO", 
            f"No schema version specified in metadata. Using validator default v{schema_version}"))
    
    return issues

SCHEMAS = {m: load_schema(m) for m in MODALITY_PATTERNS}

# ----------------------------
# Inherited Metadata System
# ----------------------------
def collect_inherited_metadata(file_path, root_dir):
    """Collect metadata that should be inherited from parent directories"""
    inherited_data = {}
    
    # Get relative path from root
    rel_path = os.path.relpath(file_path, root_dir)
    path_parts = rel_path.split(os.sep)
    
    # Build list of potential inheritance paths
    inheritance_paths = []
    current_path = root_dir
    
    # Add dataset-level inheritance
    inheritance_paths.append(os.path.join(root_dir, "task-*_stim.json"))
    
    # Walk up the directory tree
    for i, part in enumerate(path_parts[:-1]):  # exclude filename
        current_path = os.path.join(current_path, part)
        
        # Look for generic inheritance files
        inheritance_patterns = [
            os.path.join(current_path, "*_stim.json"),
            os.path.join(current_path, "stim.json")
        ]
        
        # Add subject-specific inheritance
        if part.startswith("sub-"):
            inheritance_patterns.append(os.path.join(current_path, f"{part}_stim.json"))
        
        inheritance_paths.extend(inheritance_patterns)
    
    # Collect metadata from inheritance files (most general to most specific)
    for pattern in inheritance_paths:
        if "*" in pattern:
            import glob
            matching_files = glob.glob(pattern)
        else:
            matching_files = [pattern] if os.path.exists(pattern) else []
        
        for inheritance_file in matching_files:
            if os.path.exists(inheritance_file):
                try:
                    with open(inheritance_file) as f:
                        inheritance_data = json.load(f)
                    # Merge with existing inherited data (later files override earlier ones)
                    inherited_data.update(inheritance_data)
                except (json.JSONDecodeError, IOError):
                    continue
    
    return inherited_data

def merge_metadata(inherited_data, sidecar_data):
    """Merge inherited metadata with sidecar metadata (sidecar takes precedence)"""
    merged = inherited_data.copy()
    
    def deep_merge(base_dict, override_dict):
        """Recursively merge dictionaries"""
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    deep_merge(merged, sidecar_data)
    return merged

# ----------------------------
# Participants.tsv Integration
# ----------------------------
def load_participants_info(root_dir):
    """Load and parse participants.tsv file"""
    participants_path = os.path.join(root_dir, "participants.tsv")
    participants_info = {}
    
    if not os.path.exists(participants_path):
        return participants_info, ["Missing participants.tsv file"]
    
    issues = []
    try:
        with open(participants_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            issues.append("participants.tsv is empty")
            return participants_info, issues
        
        # Parse header
        header = lines[0].strip().split('\t')
        if 'participant_id' not in header:
            issues.append("participants.tsv missing required 'participant_id' column")
            return participants_info, issues
        
        participant_id_idx = header.index('participant_id')
        
        # Parse data rows
        for line_num, line in enumerate(lines[1:], 2):
            if line.strip():  # Skip empty lines
                values = line.strip().split('\t')
                if len(values) > participant_id_idx:
                    participant_id = values[participant_id_idx]
                    
                    # Create participant info dict
                    participant_data = {}
                    for i, value in enumerate(values):
                        if i < len(header):
                            participant_data[header[i]] = value
                    
                    participants_info[participant_id] = participant_data
                else:
                    issues.append(f"participants.tsv line {line_num}: insufficient columns")
    
    except Exception as e:
        issues.append(f"Error reading participants.tsv: {e}")
    
    return participants_info, issues

def validate_participants_consistency(stats, participants_info):
    """Validate consistency between found subjects and participants.tsv"""
    issues = []
    
    if not participants_info:
        return issues  # Already handled in load_participants_info
    
    # Convert subject IDs to participant_id format (sub-001 -> sub-001)
    found_subjects = set(stats.subjects)
    listed_participants = set(participants_info.keys())
    
    # Check for subjects in data but not in participants.tsv
    missing_in_participants = found_subjects - listed_participants
    for subject in missing_in_participants:
        issues.append(("WARNING", f"Subject {subject} found in data but not listed in participants.tsv"))
    
    # Check for participants listed but not found in data
    missing_in_data = listed_participants - found_subjects
    for participant in missing_in_data:
        issues.append(("WARNING", f"Participant {participant} listed in participants.tsv but no data found"))
    
    return issues

# ----------------------------
# Helper: validate sidecar JSON (enhanced with inheritance)
# ----------------------------
def validate_sidecar(file_path, schema, root_dir):
    sidecar = file_path.replace(os.path.splitext(file_path)[1], ".json")
    issues = []
    
    if not os.path.exists(sidecar):
        issues.append(("ERROR", f"Missing sidecar for {file_path}"))
        return issues
    
    try:
        # Load sidecar data
        with open(sidecar) as f:
            sidecar_data = json.load(f)
        
        # Collect inherited metadata
        inherited_data = collect_inherited_metadata(file_path, root_dir)
        
        # Merge inherited and sidecar metadata
        complete_metadata = merge_metadata(inherited_data, sidecar_data)
        
        # Validate schema version compatibility
        if schema:
            version_issues = validate_schema_version(complete_metadata, schema)
            issues.extend(version_issues)
            
            # Validate against schema
            validate(instance=complete_metadata, schema=schema)
            
        # Store complete metadata for potential future use
        # (could be used for database export, cross-file validation, etc.)
        
    except ValidationError as e:
        issues.append(("ERROR", f"{sidecar} schema error: {e.message}"))
    except json.JSONDecodeError:
        issues.append(("ERROR", f"{sidecar} is not valid JSON"))
    except Exception as e:
        issues.append(("ERROR", f"Error processing {sidecar}: {e}"))
    
    return issues

# ----------------------------
# Dataset Statistics Class
# ----------------------------
class DatasetStats:
    def __init__(self):
        self.subjects = set()
        self.sessions = set()
        self.modalities = {}  # modality -> file count
        self.tasks = set()
        self.total_files = 0
        self.sidecar_files = 0
        # For consistency checking
        self.subject_data = {}  # subject_id -> {sessions: {}, modalities: set(), tasks: set()}
        
    def add_file(self, subject_id, session_id, modality, task, filename):
        self.subjects.add(subject_id)
        if session_id:
            self.sessions.add(f"{subject_id}/{session_id}")
        if modality not in self.modalities:
            self.modalities[modality] = 0
        self.modalities[modality] += 1
        if task:
            self.tasks.add(task)
        self.total_files += 1
        
        # Check for sidecar
        if filename.endswith('.json'):
            self.sidecar_files += 1
        
        # Track per-subject data for consistency checking
        if subject_id not in self.subject_data:
            self.subject_data[subject_id] = {
                'sessions': set(),
                'modalities': set(),
                'tasks': set(),
                'session_data': {}  # session_id -> {modalities: set(), tasks: set()}
            }
        
        subject_info = self.subject_data[subject_id]
        subject_info['modalities'].add(modality)
        if task:
            subject_info['tasks'].add(task)
        
        if session_id:
            subject_info['sessions'].add(session_id)
            if session_id not in subject_info['session_data']:
                subject_info['session_data'][session_id] = {
                    'modalities': set(),
                    'tasks': set()
                }
            subject_info['session_data'][session_id]['modalities'].add(modality)
            if task:
                subject_info['session_data'][session_id]['tasks'].add(task)

    def check_consistency(self):
        """Check for consistency across subjects and return warnings"""
        warnings = []
        
        if len(self.subjects) < 2:
            return warnings  # Can't check consistency with less than 2 subjects
        
        # Separate subjects with and without sessions
        subjects_with_sessions = {}
        subjects_without_sessions = {}
        
        for subject_id, data in self.subject_data.items():
            if data['sessions']:
                subjects_with_sessions[subject_id] = data
            else:
                subjects_without_sessions[subject_id] = data
        
        # Check consistency within session-based subjects
        if len(subjects_with_sessions) > 1:
            warnings.extend(self._check_session_consistency(subjects_with_sessions))
        
        # Check consistency within non-session subjects
        if len(subjects_without_sessions) > 1:
            warnings.extend(self._check_non_session_consistency(subjects_without_sessions))
        
        # Warn if mixing session and non-session structures
        if subjects_with_sessions and subjects_without_sessions:
            warnings.append(("WARNING", f"Mixed session structure: {len(subjects_with_sessions)} subjects have sessions, {len(subjects_without_sessions)} don't"))
        
        return warnings
    
    def _check_session_consistency(self, subjects_with_sessions):
        """Check consistency among subjects with sessions"""
        warnings = []
        
        # Find all unique sessions across subjects
        all_sessions = set()
        for data in subjects_with_sessions.values():
            all_sessions.update(data['sessions'])
        
        # Check if all subjects have all sessions
        for subject_id, data in subjects_with_sessions.items():
            missing_sessions = all_sessions - data['sessions']
            if missing_sessions:
                for session in missing_sessions:
                    warnings.append(("WARNING", f"Subject {subject_id} missing session {session}"))
        
        # For each session, check modality/task consistency
        for session in all_sessions:
            session_modalities = set()
            session_tasks = set()
            subjects_with_this_session = []
            
            # Collect all modalities and tasks for this session
            for subject_id, data in subjects_with_sessions.items():
                if session in data['sessions'] and session in data['session_data']:
                    session_data = data['session_data'][session]
                    session_modalities.update(session_data['modalities'])
                    session_tasks.update(session_data['tasks'])
                    subjects_with_this_session.append(subject_id)
            
            # Check each subject has all modalities/tasks for this session
            for subject_id in subjects_with_this_session:
                if session in subjects_with_sessions[subject_id]['session_data']:
                    subject_session_data = subjects_with_sessions[subject_id]['session_data'][session]
                    
                    missing_modalities = session_modalities - subject_session_data['modalities']
                    missing_tasks = session_tasks - subject_session_data['tasks']
                    
                    for modality in missing_modalities:
                        warnings.append(("WARNING", f"Subject {subject_id} session {session} missing {modality} data"))
                    
                    for task in missing_tasks:
                        warnings.append(("WARNING", f"Subject {subject_id} session {session} missing task {task}"))
        
        return warnings
    
    def _check_non_session_consistency(self, subjects_without_sessions):
        """Check consistency among subjects without sessions"""
        warnings = []
        
        # Find all modalities and tasks across subjects
        all_modalities = set()
        all_tasks = set()
        for data in subjects_without_sessions.values():
            all_modalities.update(data['modalities'])
            all_tasks.update(data['tasks'])
        
        # Check each subject has all modalities and tasks
        for subject_id, data in subjects_without_sessions.items():
            missing_modalities = all_modalities - data['modalities']
            missing_tasks = all_tasks - data['tasks']
            
            for modality in missing_modalities:
                warnings.append(("WARNING", f"Subject {subject_id} missing {modality} data"))
            
            for task in missing_tasks:
                warnings.append(("WARNING", f"Subject {subject_id} missing task {task}"))
        
        return warnings

# ----------------------------
# Main validator
# ----------------------------
def validate_dataset(root_dir):
    issues = []
    stats = DatasetStats()

    # 1. Dataset-level checks
    dataset_desc_path = os.path.join(root_dir, "dataset_description.json")
    if not os.path.exists(dataset_desc_path):
        issues.append(("ERROR", "Missing dataset_description.json"))
    
    # 2. Load and validate participants.tsv
    participants_info, participant_issues = load_participants_info(root_dir)
    for issue in participant_issues:
        issues.append(("WARNING", issue))

    # 3. Walk through subject directories
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item.startswith("sub-"):
            # This is a subject directory
            subject_issues = validate_subject(item_path, item, stats, root_dir)
            issues += subject_issues

    # 4. Check cross-subject consistency
    consistency_warnings = stats.check_consistency()
    issues += consistency_warnings
    
    # 5. Validate participants.tsv consistency
    participant_consistency_issues = validate_participants_consistency(stats, participants_info)
    issues += participant_consistency_issues

    return issues, stats

def validate_subject(subject_dir, subject_id, stats, root_dir):
    """Validate a single subject directory"""
    issues = []
    
    for item in os.listdir(subject_dir):
        item_path = os.path.join(subject_dir, item)
        if os.path.isdir(item_path):
            if item.startswith("ses-"):
                # Session directory
                issues += validate_session(item_path, subject_id, item, stats, root_dir)
            elif item in MODALITY_PATTERNS:
                # Direct modality directory (no sessions)
                issues += validate_modality_dir(item_path, subject_id, None, item, stats, root_dir)
    
    return issues

def validate_session(session_dir, subject_id, session_id, stats, root_dir):
    """Validate a single session directory"""
    issues = []
    
    for item in os.listdir(session_dir):
        item_path = os.path.join(session_dir, item)
        if os.path.isdir(item_path) and item in MODALITY_PATTERNS:
            issues += validate_modality_dir(item_path, subject_id, session_id, item, stats, root_dir)
    
    return issues

def validate_modality_dir(modality_dir, subject_id, session_id, modality, stats, root_dir):
    """Validate files in a modality directory"""
    issues = []
    pattern = re.compile(MODALITY_PATTERNS[modality])
    schema = SCHEMAS.get(modality)
    
    for fname in os.listdir(modality_dir):
        file_path = os.path.join(modality_dir, fname)
        if os.path.isfile(file_path):
            # Extract task from filename if possible
            task = None
            if "_task-" in fname:
                task_match = re.search(r'_task-([a-zA-Z0-9]+)', fname)
                if task_match:
                    task = task_match.group(1)
            
            # Add to stats for all files in modality directory
            stats.add_file(subject_id, session_id, modality, task, fname)
            
            if pattern.match(fname):
                # Check naming convention
                base, ext = os.path.splitext(fname)
                if not BIDS_REGEX.match(base):
                    issues.append(("ERROR", f"Invalid filename: {fname} in {modality_dir}"))
                
                # Validate expected subject/session in filename
                if subject_id not in fname:
                    issues.append(("ERROR", f"Filename {fname} doesn't contain subject ID {subject_id}"))
                
                if session_id and session_id not in fname:
                    issues.append(("ERROR", f"Filename {fname} doesn't contain session ID {session_id}"))
                
                # Check sidecar schema (now with inheritance)
                issues += validate_sidecar(file_path, schema, root_dir)
    
    return issues

# ----------------------------
# Summary Display Functions
# ----------------------------
def print_dataset_summary(dataset_path, stats):
    """Print a comprehensive dataset summary like BIDS validator"""
    print("\n" + "="*60)
    print("🗂️  DATASET SUMMARY")
    print("="*60)
    
    # Dataset info
    dataset_name = os.path.basename(os.path.abspath(dataset_path))
    print(f"📁 Dataset: {dataset_name}")
    
    # Subject and session counts
    num_subjects = len(stats.subjects)
    num_sessions = len(stats.sessions)
    has_sessions = num_sessions > 0
    
    print(f"👥 Subjects: {num_subjects}")
    if has_sessions:
        print(f"📋 Sessions: {num_sessions}")
        # Calculate sessions per subject
        sessions_per_subject = {}
        for session in stats.sessions:
            subj = session.split('/')[0]
            sessions_per_subject[subj] = sessions_per_subject.get(subj, 0) + 1
        avg_sessions = sum(sessions_per_subject.values()) / len(sessions_per_subject) if sessions_per_subject else 0
        print(f"📊 Sessions per subject: {avg_sessions:.1f} (avg)")
    else:
        print("📋 Sessions: No session structure detected")
    
    # Modality breakdown
    print(f"\n🎯 MODALITIES ({len(stats.modalities)} found):")
    if stats.modalities:
        for modality, count in sorted(stats.modalities.items()):
            schema_status = "✅" if SCHEMAS.get(modality) else "❌"
            print(f"  {schema_status} {modality}: {count} files")
    else:
        print("  No modality data found")
    
    # Task breakdown
    print(f"\n📝 TASKS ({len(stats.tasks)} found):")
    if stats.tasks:
        for task in sorted(stats.tasks):
            print(f"  • {task}")
    else:
        print("  No tasks detected")
    
    # File statistics
    data_files = stats.total_files - stats.sidecar_files
    print(f"\n📄 FILES:")
    print(f"  • Data files: {data_files}")
    print(f"  • Sidecar files: {stats.sidecar_files}")
    print(f"  • Total files: {stats.total_files}")

def print_validation_results(problems):
    """Print validation results with proper categorization"""
    if not problems:
        print("\n" + "="*60)
        print("✅ VALIDATION RESULTS")
        print("="*60)
        print("🎉 No issues found! Dataset is valid.")
        return
    
    # Categorize problems
    errors = [msg for level, msg in problems if level == "ERROR"]
    warnings = [msg for level, msg in problems if level == "WARNING"]
    infos = [msg for level, msg in problems if level == "INFO"]
    
    print("\n" + "="*60)
    print("🔍 VALIDATION RESULTS")
    print("="*60)
    
    if errors:
        print(f"\n🔴 ERRORS ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i:2d}. {error}")
    
    if warnings:
        print(f"\n🟡 WARNINGS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i:2d}. {warning}")
    
    if infos:
        print(f"\n🔵 INFO ({len(infos)}):")
        for i, info in enumerate(infos, 1):
            print(f"  {i:2d}. {info}")
    
    # Summary line
    print(f"\n📊 SUMMARY: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
    
    if errors:
        print("❌ Dataset validation failed due to errors.")
    else:
        print("⚠️  Dataset has warnings but no critical errors.")

def print_schema_info(modality):
    """Prints a user-friendly description of a schema."""
    schema = SCHEMAS.get(modality)
    if not schema:
        print(f"❌ Schema for modality '{modality}' not found.")
        return

    print("\n" + "="*60)
    print(f"📄 SCHEMA DETAILS FOR: {modality.upper()}")
    print("="*60)
    
    # Schema metadata
    if "title" in schema:
        print(f"  Title: {schema['title']}")
    if "description" in schema:
        print(f"  Description: {schema['description']}")
    
    # Version information
    version = schema.get('version', 'unknown')
    schema_id = schema.get('$id', 'unknown')
    print(f"  Version: {version}")
    print(f"  Schema ID: {schema_id}")
    
    print("\nFIELDS:")
    
    required_fields = schema.get("required", [])
    
    def print_properties(properties, required_list, indent_level=0):
        """Recursively print properties with proper indentation"""
        indent = "  " * (indent_level + 1)
        
        for prop, details in properties.items():
            is_required = "REQUIRED" if prop in required_list else "OPTIONAL"
            prop_type = details.get('type', 'N/A')
            
            print(f"\n{indent}- {prop} ({prop_type}) - [{is_required}]")
            
            if "description" in details:
                print(f"{indent}  {details['description']}")
            
            if "enum" in details:
                enum_values = details['enum']
                if len(enum_values) <= 5:
                    print(f"{indent}  Options: {', '.join(map(str, enum_values))}")
                else:
                    print(f"{indent}  Options: {', '.join(map(str, enum_values[:3]))}... ({len(enum_values)} total)")
            
            if "minimum" in details:
                print(f"{indent}  Minimum: {details['minimum']}")
            if "maximum" in details:
                print(f"{indent}  Maximum: {details['maximum']}")
            if "default" in details:
                print(f"{indent}  Default: {details['default']}")
            
            # Handle nested objects
            if prop_type == "object" and "properties" in details:
                nested_required = details.get("required", [])
                print_properties(details["properties"], nested_required, indent_level + 1)
    
    print_properties(schema.get("properties", {}), required_fields)

def list_schema_versions():
    """List all available schema versions"""
    print("\n" + "="*60)
    print("📚 AVAILABLE SCHEMA VERSIONS")
    print("="*60)
    
    for modality, schema in SCHEMAS.items():
        if schema:
            version = schema.get('version', 'unknown')
            schema_id = schema.get('$id', 'N/A')
            print(f"  {modality:12} v{version:8} ({schema_id})")
        else:
            print(f"  {modality:12} {'ERROR':8} (Schema not found)")
    
    print(f"\n📋 Schema versioning follows semantic versioning (MAJOR.MINOR.PATCH)")
    print(f"   • MAJOR: Breaking changes (incompatible)")
    print(f"   • MINOR: New features (backward compatible)")  
    print(f"   • PATCH: Bug fixes (backward compatible)")

# ----------------------------
# CLI entry point
# ----------------------------
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Psycho-Validator (BIDS-inspired)")
    parser.add_argument("dataset", nargs='?', default=None, help="Path to dataset root")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Show detailed validation information")
    parser.add_argument("--schema-info", metavar="MODALITY",
                       help="Display schema details for a specific modality")
    parser.add_argument("--list-versions", action="store_true",
                       help="List all available schema versions")
    parser.add_argument("--check-compatibility", nargs=2, metavar=('SCHEMA_VERSION', 'REQUIRED_VERSION'),
                       help="Check if a schema version is compatible with a required version")
    args = parser.parse_args()

    if args.schema_info:
        print_schema_info(args.schema_info)
        sys.exit(0)
    
    if args.list_versions:
        list_schema_versions()
        sys.exit(0)
    
    if args.check_compatibility:
        schema_version, required_version = args.check_compatibility
        is_compat = is_compatible_version(schema_version, required_version)
        print(f"Schema version {schema_version} {'IS' if is_compat else 'IS NOT'} compatible with required version {required_version}")
        sys.exit(0 if is_compat else 1)

    if not args.dataset:
        parser.error("the following arguments are required: dataset")

    if not os.path.exists(args.dataset):
        print(f"❌ Dataset directory not found: {args.dataset}")
        sys.exit(1)

    print(f"🔍 Validating dataset: {args.dataset}")
    if args.verbose:
        print(f"📁 Scanning for modalities: {list(MODALITY_PATTERNS.keys())}")
        print(f"📋 Available schemas: {[k for k, v in SCHEMAS.items() if v is not None]}")
    
    problems, stats = validate_dataset(args.dataset)

    # Print comprehensive summary
    print_dataset_summary(args.dataset, stats)
    
    # Print validation results
    print_validation_results(problems)
    
    # Exit with appropriate code
    error_count = sum(1 for level, _ in problems if level == "ERROR")
    if error_count > 0:
        sys.exit(1)