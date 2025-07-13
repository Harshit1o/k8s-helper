#!/usr/bin/env python3
"""
Test script to verify k8s-helper CLI functionality
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return its output"""
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        print("-" * 50)
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        print("-" * 50)
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("K8S-HELPER CLI FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test version option
    tests = [
        ("k8s-helper --version", "Version option"),
        ("k8s-helper --help", "Help option"),
        ("k8s-helper list-pods --help", "Subcommand help"),
        ("k8s-helper config --show", "Config show (should work even without k8s cluster)"),
    ]
    
    results = []
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {desc}")
    
    all_passed = all(success for _, success in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
