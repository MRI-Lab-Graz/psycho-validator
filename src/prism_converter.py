"""
PRISM <-> BIDS Converter
Handles conversion between PRISM (nested) and BIDS (flat) metadata formats.
"""

import json
import os
from copy import deepcopy

# Mapping definitions
# Format: "BIDS_Field": ("PRISM.Path.To.Field", DefaultValue)
# or "BIDS_Field": ("PRISM.Path", transformation_function)

EYETRACKING_MAPPING = {
    "SamplingFrequency": "Technical.SamplingRate",
    "Manufacturer": "Metadata.Equipment.Manufacturer",
    "ManufacturersModelName": "Metadata.Equipment.Model",
    "TaskName": "Study.Task",
    "RecordedEye": "Technical.EyeTracked",
    "PupilPositionType": "Technical.PupilPositionType",  # Assuming this exists or will exist
    "EyeTrackingMethod": "Technical.TrackingMode",
}

EEG_MAPPING = {
    "SamplingFrequency": "Technical.SamplingRate",
    "PowerLineFrequency": "Technical.FilterSettings.NotchFilter",
    "EEGChannelCount": "Technical.ChannelCount",
    "EEGReference": "Technical.ReferenceType",
    "Manufacturer": "Metadata.Equipment.Manufacturer",
    "ManufacturersModelName": "Metadata.Equipment.Model",
    "TaskName": "Study.Task",
    "InstitutionName": "Metadata.Institution",
}

DATASET_DESCRIPTION_MAPPING = {
    "Name": "Name",
    "BIDSVersion": "BIDSVersion",
    "DatasetType": "DatasetType",
    "License": "License",
    "Authors": "Authors",  # PRISM allows objects, BIDS expects strings. Needs special handling.
    "Acknowledgements": "Acknowledgements",
    "Funding": "Funding",
    "ReferencesAndLinks": "ReferencesAndLinks",
    "DatasetDOI": "DatasetDOI",
}

def get_nested_value(data, path):
    """Retrieve value from nested dictionary using dot notation."""
    keys = path.split(".")
    val = data
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return None
    return val

def set_nested_value(data, path, value):
    """Set value in nested dictionary using dot notation, creating dicts as needed."""
    keys = path.split(".")
    current = data
    for i, k in enumerate(keys[:-1]):
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value

def prism_to_bids(prism_data, modality):
    """Convert PRISM nested dictionary to BIDS flat dictionary."""
    bids_data = {}
    mapping = {}
    
    if modality == "eyetracking":
        mapping = EYETRACKING_MAPPING
    elif modality == "eeg":
        mapping = EEG_MAPPING
    elif modality == "dataset_description":
        mapping = DATASET_DESCRIPTION_MAPPING
    
    for bids_key, prism_path in mapping.items():
        val = get_nested_value(prism_data, prism_path)
        if val is not None:
            # Special handling for Authors in dataset_description
            if modality == "dataset_description" and bids_key == "Authors":
                if isinstance(val, list):
                    # Convert object authors to string authors if needed
                    bids_data[bids_key] = [
                        a["name"] if isinstance(a, dict) and "name" in a else str(a)
                        for a in val
                    ]
            else:
                bids_data[bids_key] = val
            
    return bids_data

def bids_to_prism(bids_data, modality):
    """Convert BIDS flat dictionary to PRISM nested dictionary structure."""
    prism_data = {}
    mapping = {}
    
    if modality == "eyetracking":
        mapping = EYETRACKING_MAPPING
    elif modality == "eeg":
        mapping = EEG_MAPPING
    elif modality == "dataset_description":
        mapping = DATASET_DESCRIPTION_MAPPING
        
    for bids_key, prism_path in mapping.items():
        if bids_key in bids_data:
            set_nested_value(prism_data, prism_path, bids_data[bids_key])
            
    # Add required PRISM structure stubs if missing (simplified)
    if modality != "dataset_description":
        if "Metadata" not in prism_data:
            prism_data["Metadata"] = {}
        if "SchemaVersion" not in prism_data.get("Metadata", {}):
            set_nested_value(prism_data, "Metadata.SchemaVersion", "1.0.0")
            
    return prism_data
