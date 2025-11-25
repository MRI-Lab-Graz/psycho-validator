import os
import shutil
from pathlib import Path

def move_ecg_files():
    base_dir = Path("/Volumes/Evo/software/psycho-validator/PK01")
    rawdata_dir = base_dir / "rawdata"
    derivatives_dir = base_dir / "derivatives" / "ecg"
    
    print(f"Scanning {rawdata_dir} for ECG files...")
    
    # Find all ECG files
    ecg_files = list(rawdata_dir.rglob("*task-ecg*"))
    
    if not ecg_files:
        print("No ECG files found.")
        return

    print(f"Found {len(ecg_files)} files.")
    
    for file_path in ecg_files:
        # Parse path to get sub and ses
        # Expected path: PK01/rawdata/sub-X/ses-Y/beh/filename
        
        parts = file_path.parts
        
        try:
            sub = next(p for p in parts if p.startswith("sub-"))
            ses = next(p for p in parts if p.startswith("ses-"))
        except StopIteration:
            # If it's a root file like task-ecg_beh.json
            if file_path.parent == rawdata_dir:
                 print(f"Moving root file {file_path}")
                 # Move root file to derivatives/ecg root?
                 # Or maybe just leave it? 
                 # If it's a sidecar for the task, it should probably go to derivatives/ecg/
                 new_path = derivatives_dir / file_path.name.replace("_beh", "_physio")
                 derivatives_dir.mkdir(parents=True, exist_ok=True)
                 shutil.move(str(file_path), str(new_path))
                 continue
            
            print(f"Skipping {file_path}: Could not extract sub/ses")
            continue
            
        # Construct new directory
        new_dir = derivatives_dir / sub / ses
        new_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct new filename
        # Replace _beh with _physio
        new_name = file_path.name.replace("_beh", "_physio")
        new_path = new_dir / new_name
        
        print(f"Moving {file_path} -> {new_path}")
        shutil.move(str(file_path), str(new_path))
        
        # Check if parent directory (beh) is empty and remove it if so
        parent_dir = file_path.parent
        if parent_dir.name == "beh" and not any(parent_dir.iterdir()):
            print(f"Removing empty directory {parent_dir}")
            parent_dir.rmdir()

if __name__ == "__main__":
    move_ecg_files()
