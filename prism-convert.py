#!/usr/bin/env python3
"""
PRISM Conversion Tool
Converts dataset metadata between PRISM (Rich) and BIDS (Standard) formats.
"""

import os
import sys
import json
import argparse

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.insert(0, src_path)

from prism_converter import prism_to_bids, bids_to_prism
from validator import MODALITY_PATTERNS

def convert_dataset(root_dir, target_format="bids", verbose=False):
    """Convert all sidecars in the dataset."""
    
    print(f"🔄 Converting dataset to {target_format.upper()}...")
    count = 0
    
    # Handle dataset_description.json
    desc_path = os.path.join(root_dir, "dataset_description.json")
    if os.path.exists(desc_path):
        convert_file(desc_path, "dataset_description", target_format, verbose)
        count += 1

    # Walk through dataset
    for root, dirs, files in os.walk(root_dir):
        for fname in files:
            if not fname.endswith(".json"):
                continue
                
            if fname == "dataset_description.json":
                continue # Already handled
                
            # Determine modality from filename
            modality = None
            for mod, pattern in MODALITY_PATTERNS.items():
                # Simple check: if modality name is in filename (e.g. _eeg.json)
                if f"_{mod}" in fname:
                    modality = mod
                    break
            
            if modality:
                file_path = os.path.join(root, fname)
                if convert_file(file_path, modality, target_format, verbose):
                    count += 1
                    
    print(f"✅ Converted {count} files.")

def convert_file(file_path, modality, target_format, verbose):
    """Convert a single file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        new_data = None
        
        # Check if file is already in target format (heuristic)
        is_prism = "Technical" in data or "Metadata" in data
        
        if target_format == "bids":
            if is_prism:
                new_data = prism_to_bids(data, modality)
            elif verbose:
                print(f"  Skipping {os.path.basename(file_path)} (already flat/BIDS?)")
                
        elif target_format == "prism":
            if not is_prism:
                new_data = bids_to_prism(data, modality)
            elif verbose:
                print(f"  Skipping {os.path.basename(file_path)} (already PRISM?)")
        
        if new_data:
            with open(file_path, 'w') as f:
                json.dump(new_data, f, indent=2)
            if verbose:
                print(f"  Converted {os.path.basename(file_path)}")
            return True
            
    except Exception as e:
        print(f"❌ Error converting {file_path}: {e}")
        
    return False

def main():
    parser = argparse.ArgumentParser(description="Convert dataset metadata between PRISM and BIDS formats")
    parser.add_argument("dataset", help="Path to dataset root")
    parser.add_argument("--to-bids", action="store_true", help="Convert PRISM -> BIDS (Flatten)")
    parser.add_argument("--to-prism", action="store_true", help="Convert BIDS -> PRISM (Enrich/Nest)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"Error: Dataset not found at {args.dataset}")
        sys.exit(1)
        
    if args.to_bids and args.to_prism:
        print("Error: Cannot specify both --to-bids and --to-prism")
        sys.exit(1)
        
    if not args.to_bids and not args.to_prism:
        print("Error: Must specify either --to-bids or --to-prism")
        sys.exit(1)
        
    target = "bids" if args.to_bids else "prism"
    convert_dataset(args.dataset, target, args.verbose)

if __name__ == "__main__":
    main()
