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

def main():
    base_dir = "test_dataset"
    
    # Create realistic dummy files
    files_to_create = [
        {
            "path": "sub-001/ses-001/image/sub-001_ses-001_task-facerecognition_run-01_stim.png",
            "type": "image",
            "size": (800, 600)
        },
        {
            "path": "sub-001/ses-001/audio/sub-001_ses-001_task-soundrecognition_run-01_stim.wav",
            "type": "audio",
            "duration": 2.5
        },
        {
            "path": "sub-003/ses-001/image/sub-003_ses-001_task-facerecognition_run-02_stim.jpg",
            "type": "image",
            "size": (1024, 768)
        }
    ]
    
    for file_info in files_to_create:
        filepath = os.path.join(base_dir, file_info["path"])
        
        if file_info["type"] == "image":
            width, height = file_info["size"]
            create_dummy_image(filepath, width, height)
            print(f"Created dummy image: {filepath}")
        
        elif file_info["type"] == "audio":
            duration = file_info["duration"]
            create_dummy_audio(filepath, duration)
            print(f"Created dummy audio: {filepath}")

if __name__ == "__main__":
    try:
        main()
        print("✅ Dummy files created successfully!")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install Pillow numpy")
    except Exception as e:
        print(f"❌ Error creating files: {e}")
