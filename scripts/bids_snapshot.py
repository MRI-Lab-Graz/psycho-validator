#!/usr/bin/env python3
"""
Create a BIDS-compliant snapshot of a PRISM dataset.
Useful for running BIDS-Apps (like fMRIPrep) without modifying the source dataset.

Usage:
    python3 scripts/bids_snapshot.py /path/to/prism_dataset /path/to/output_snapshot
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def create_snapshot(source_dir, target_dir, verbose=False):
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not source_path.exists():
        print(f"❌ Source directory not found: {source_path}")
        sys.exit(1)

    if target_path.exists():
        print(f"❌ Target directory already exists: {target_path}")
        print("   Please remove it or specify a new path.")
        sys.exit(1)

    print(f"📸 Creating BIDS snapshot...")
    print(f"   Source: {source_path}")
    print(f"   Target: {target_path}")

    # 1. Create directory structure and hardlink files
    # We use 'cp -al' (archive, link) to preserve attributes and use hardlinks
    # This is fast and uses minimal disk space for large data files
    try:
        if sys.platform == "darwin":
            # macOS cp -al works
            subprocess.run(["cp", "-al", str(source_path), str(target_path)], check=True)
        else:
            # Linux cp -al works
            subprocess.run(["cp", "-al", str(source_path), str(target_path)], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to create hardlink copy. Falling back to standard copy (slower)...")
        shutil.copytree(source_path, target_path)

    # 2. Break hardlinks for JSON files
    # We must do this because we are going to modify them, and we don't want to change the source!
    print("🔨 Preparing metadata for conversion...")
    json_files = list(target_path.rglob("*.json"))
    
    for json_file in json_files:
        # Read content
        try:
            content = json_file.read_bytes()
            # Remove hardlink
            json_file.unlink()
            # Write back as new file
            json_file.write_bytes(content)
        except Exception as e:
            if verbose:
                print(f"   Warning: Could not process {json_file}: {e}")

    # 3. Run PRISM -> BIDS conversion on the target
    print("🔄 Converting metadata to BIDS format...")
    
    # Locate prism-convert.py (assuming it's in the repo root)
    repo_root = Path(__file__).parent.parent
    converter_script = repo_root / "prism-convert.py"
    
    if not converter_script.exists():
        print(f"❌ Could not find prism-convert.py at {converter_script}")
        sys.exit(1)

    cmd = [sys.executable, str(converter_script), str(target_path), "--to-bids"]
    if verbose:
        cmd.append("-v")
        
    result = subprocess.run(cmd, capture_output=not verbose)
    
    if result.returncode != 0:
        print("❌ Conversion failed!")
        if not verbose:
            print(result.stderr.decode())
        sys.exit(1)

    print(f"✅ Snapshot created successfully at: {target_path}")
    print(f"   You can now run BIDS-Apps on this directory.")
    print(f"   Example: fmriprep-docker {target_path} {target_path}/derivatives participant")

def main():
    parser = argparse.ArgumentParser(description="Create a BIDS-compliant snapshot of a PRISM dataset")
    parser.add_argument("source", help="Path to source PRISM dataset")
    parser.add_argument("target", help="Path to create snapshot")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    create_snapshot(args.source, args.target, args.verbose)

if __name__ == "__main__":
    main()
