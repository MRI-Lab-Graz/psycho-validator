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
    
    participants_path = os.path.join(root_dir, "participants.tsv")
    if not os.path.exists(participants_path):
        issues.append(("WARNING", "Missing participants.tsv"))

    # 2. Walk through subject directories
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item.startswith("sub-"):
            # This is a subject directory
            subject_issues = validate_subject(item_path, item, stats)
            issues += subject_issues

    # 3. Check cross-subject consistency
    consistency_warnings = stats.check_consistency()
    issues += consistency_warnings

    return issues, stats

def validate_subject(subject_dir, subject_id, stats):
    """Validate a single subject directory"""
    issues = []
    
    for item in os.listdir(subject_dir):
        item_path = os.path.join(subject_dir, item)
        if os.path.isdir(item_path):
            if item.startswith("ses-"):
                # Session directory
                issues += validate_session(item_path, subject_id, item, stats)
            elif item in MODALITY_PATTERNS:
                # Direct modality directory (no sessions)
                issues += validate_modality_dir(item_path, subject_id, None, item, stats)
    
    return issues

def validate_session(session_dir, subject_id, session_id, stats):
    """Validate a single session directory"""
    issues = []
    
    for item in os.listdir(session_dir):
        item_path = os.path.join(session_dir, item)
        if os.path.isdir(item_path) and item in MODALITY_PATTERNS:
            issues += validate_modality_dir(item_path, subject_id, session_id, item, stats)
    
    return issues

def validate_modality_dir(modality_dir, subject_id, session_id, modality, stats):
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
                
                # Check sidecar schema
                issues += validate_sidecar(file_path, schema)
    
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
    
    # Summary line
    print(f"\n📊 SUMMARY: {len(errors)} errors, {len(warnings)} warnings")
    
    if errors:
        print("❌ Dataset validation failed due to errors.")
    else:
        print("⚠️  Dataset has warnings but no critical errors.")

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
    
    problems, stats = validate_dataset(args.dataset)

    # Print comprehensive summary
    print_dataset_summary(args.dataset, stats)
    
    # Print validation results
    print_validation_results(problems)
    
    # Exit with appropriate code
    error_count = sum(1 for level, _ in problems if level == "ERROR")
    if error_count > 0:
        sys.exit(1)
