#!/usr/bin/env python3
"""
Comprehensive test script for psycho-validator
"""

import os
import sys
import subprocess

def run_validator(dataset_path):
    """Run the validator and return the results"""
    try:
        result = subprocess.run([
            sys.executable, "psycho-validator.py", dataset_path
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_scenarios():
    """Test different validation scenarios"""
    print("🧪 Testing Psycho-Validator")
    print("=" * 50)
    
    # Test 1: Valid dataset
    print("\n📋 Test 1: Validating test dataset...")
    returncode, stdout, stderr = run_validator("test_dataset")
    
    if returncode == 0:
        print("✅ Validation completed successfully")
    else:
        print("❌ Validation failed")
    
    if stdout:
        print("Output:")
        print(stdout)
    
    if stderr:
        print("Errors:")
        print(stderr)
    
    # Test 2: Missing dataset
    print("\n📋 Test 2: Testing with non-existent dataset...")
    returncode, stdout, stderr = run_validator("non_existent_dataset")
    
    if returncode != 0:
        print("✅ Correctly failed for non-existent dataset")
    else:
        print("❌ Should have failed for non-existent dataset")
    
    print("\n🎯 Summary:")
    print("- The validator should detect naming convention violations")
    print("- Missing sidecar files should be reported as errors")
    print("- Schema validation should catch missing required fields")
    print("- Valid files should pass without issues")

if __name__ == "__main__":
    test_scenarios()
