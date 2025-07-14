#!/usr/bin/env python3
"""
Comprehensive test script for k8s-helper v0.2.0 new features
"""

import subprocess
import sys
import os

def run_command(cmd, description, expect_failure=False):
    """Run a command and return its output"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Error:\n{result.stderr}")
        
        success = result.returncode == 0
        if expect_failure:
            success = not success
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"Status: {status}")
        
        return success
        
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Main test function"""
    print("K8S-HELPER v0.2.0 - NEW FEATURES TEST")
    print("=" * 60)
    
    # Use venv k8s-helper
    k8s_helper = "C:/Users/hp/OneDrive/Documents/Open-source/.venv/Scripts/k8s-helper.exe"
    
    tests = [
        # Version and help tests
        (f"{k8s_helper} --version", "Version command", False),
        (f"{k8s_helper} --help", "Main help", False),
        
        # New command help tests
        (f"{k8s_helper} create-secret --help", "Create secret help", False),
        (f"{k8s_helper} create-pvc --help", "Create PVC help", False),
        (f"{k8s_helper} service-url --help", "Service URL help", False),
        (f"{k8s_helper} create-eks-cluster --help", "EKS cluster help", False),
        (f"{k8s_helper} apply --help", "Enhanced apply help", False),
        
        # Configuration tests
        (f"{k8s_helper} config --show", "Config show", False),
    ]
    
    results = []
    for cmd, desc, expect_failure in tests:
        success = run_command(cmd, desc, expect_failure)
        results.append((desc, success))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {desc}")
    
    all_passed = all(success for _, success in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 NEW FEATURES SUMMARY:")
        print("  • EKS cluster creation")
        print("  • Kubernetes secrets management")
        print("  • PVC (Persistent Volume Claims) management")
        print("  • Service URL retrieval (including AWS ELB)")
        print("  • Enhanced apply with init containers and volume mounts")
        print("  • AWS integration with boto3")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
