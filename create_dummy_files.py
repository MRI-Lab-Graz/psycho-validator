#!/usr/bin/env python3
"""
Generate dummy test files for psycho-validator testing
"""

import os
import json
from PIL import Image
import numpy as np
import wave

def create_dummy_image(filepath, width=800, height=600):
    """Create a dummy image file"""
    # Create a random RGB image
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(filepath)

def create_dummy_audio(filepath, duration=2.0, sample_rate=44100):
    """Create a dummy WAV audio file"""
    # Generate a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440  # A4 note
    wave_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit integers
    wave_data = (wave_data * 32767).astype(np.int16)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())

def create_sidecar_json(filepath, metadata):
    """Create a JSON sidecar file with metadata"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2)

def create_dataset_files(base_dir, files_to_create):
    """Create dataset files and their sidecars"""
    for file_info in files_to_create:
        filepath = os.path.join(base_dir, file_info["path"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if file_info["type"] == "image":
            width, height = file_info["size"]
            create_dummy_image(filepath, width, height)
            print(f"Created dummy image: {filepath}")
            
            # Create sidecar JSON
            sidecar_path = os.path.splitext(filepath)[0] + ".json"
            metadata = {
                "StimulusName": file_info.get("stimulus_name", "test_stimulus"),
                "StimulusType": file_info.get("stimulus_type", "photograph"),
                "ImageType": file_info.get("image_type", "color"),
                "Resolution": [width, height],
                "IsFamiliar": file_info.get("is_familiar", False)
            }
            create_sidecar_json(sidecar_path, metadata)
            print(f"Created sidecar: {sidecar_path}")
        
        elif file_info["type"] == "audio":
            duration = file_info["duration"]
            create_dummy_audio(filepath, duration)
            print(f"Created dummy audio: {filepath}")
            
            # Create sidecar JSON
            sidecar_path = os.path.splitext(filepath)[0] + ".json"
            metadata = {
                "StimulusName": file_info.get("stimulus_name", "test_audio"),
                "StimulusType": file_info.get("stimulus_type", "tone"),
                "Duration": duration,
                "Volume": file_info.get("volume", 0.8)
            }
            create_sidecar_json(sidecar_path, metadata)
            print(f"Created sidecar: {sidecar_path}")

def create_dataset_description(base_dir, name, description):
    """Create dataset_description.json"""
    filepath = os.path.join(base_dir, "dataset_description.json")
    os.makedirs(base_dir, exist_ok=True)
    metadata = {
        "Name": name,
        "Description": description,
        "Authors": ["Psycho-Validator Demo"],
        "Version": "1.0.0"
    }
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Created dataset description: {filepath}")

def main():
    # Create consistent test dataset (no errors, no warnings)
    print("Creating consistent_test_dataset...")
    consistent_files = [
        {
            "path": "sub-001/image/sub-001_task-recognition_run-01_stim.png",
            "type": "image",
            "size": (800, 600),
            "stimulus_name": "face_001",
            "stimulus_type": "photograph",
            "image_type": "color",
            "is_familiar": True
        },
        {
            "path": "sub-001/audio/sub-001_task-recognition_run-01_stim.wav",
            "type": "audio",
            "duration": 2.0,
            "stimulus_name": "word_001",
            "stimulus_type": "spoken_word",
            "volume": 0.7
        },
        {
            "path": "sub-002/image/sub-002_task-recognition_run-01_stim.png",
            "type": "image",
            "size": (800, 600),
            "stimulus_name": "face_002",
            "stimulus_type": "photograph",
            "image_type": "color",
            "is_familiar": False
        },
        {
            "path": "sub-002/audio/sub-002_task-recognition_run-01_stim.wav",
            "type": "audio",
            "duration": 2.0,
            "stimulus_name": "word_002",
            "stimulus_type": "spoken_word",
            "volume": 0.7
        }
    ]
    
    create_dataset_description("consistent_test_dataset", "Consistent Test Dataset", 
                             "A perfectly consistent dataset for testing the psycho-validator")
    create_dataset_files("consistent_test_dataset", consistent_files)
    
    # Create original test dataset files (with errors)
    print("\nCreating additional test_dataset files...")
    test_files = [
        {
            "path": "sub-001/ses-001/image/sub-001_ses-001_task-facerecognition_run-01_stim.png",
            "type": "image",
            "size": (800, 600),
            "stimulus_name": "face_test",
            "stimulus_type": "photograph",
            "image_type": "color"
        },
        {
            "path": "sub-001/ses-001/audio/sub-001_ses-001_task-soundrecognition_run-01_stim.wav",
            "type": "audio",
            "duration": 2.5,
            "stimulus_name": "sound_test",
            "stimulus_type": "sound_effect"
        },
        {
            "path": "sub-003/ses-001/image/sub-003_ses-001_task-facerecognition_run-02_stim.jpg",
            "type": "image",
            "size": (1024, 768),
            "stimulus_name": "face_test2",
            "stimulus_type": "photograph",
            "image_type": "color"
        }
    ]
    
    create_dataset_files("test_dataset", test_files)

if __name__ == "__main__":
    try:
        main()
        print("✅ Dummy files created successfully!")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install Pillow numpy")
    except Exception as e:
        print(f"❌ Error creating files: {e}")
