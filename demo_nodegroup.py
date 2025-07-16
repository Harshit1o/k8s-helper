#!/usr/bin/env python3
"""
Demo script showing the new node group functionality in k8s-helper CLI
"""

import subprocess
import sys
import json
import time

def run_command(cmd, show_output=True):
    """Run a command and return the result"""
    print(f"💻 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if show_output:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️  Error: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, "", str(e)

def main():
    print("🚀 k8s-helper v0.2.4 - Node Group Demo")
    print("=======================================")
    
    # Show version
    print("\n📋 Version Check:")
    run_command("k8s-helper --version")
    
    # Show new create-eks-cluster options
    print("\n📋 New create-eks-cluster options:")
    run_command("k8s-helper create-eks-cluster --help")
    
    # Show new create-nodegroup command
    print("\n📋 New create-nodegroup command:")
    run_command("k8s-helper create-nodegroup --help")
    
    # Show list-nodegroups command
    print("\n📋 New list-nodegroups command:")
    run_command("k8s-helper list-nodegroups --help")
    
    print("\n🎉 Demo completed!")
    print("\n📝 Usage Examples:")
    print("   # Create cluster with automatic node group:")
    print("   k8s-helper create-eks-cluster my-cluster --create-nodegroup")
    print("\n   # Create cluster without node group:")
    print("   k8s-helper create-eks-cluster my-cluster --no-nodegroup")
    print("\n   # Create node group manually:")
    print("   k8s-helper create-nodegroup my-cluster my-nodegroup")
    print("\n   # List node groups:")
    print("   k8s-helper list-nodegroups my-cluster")
    print("\n   # Create with SPOT instances:")
    print("   k8s-helper create-eks-cluster my-cluster --capacity-type SPOT")
    print("\n   # Create with multiple instance types:")
    print("   k8s-helper create-eks-cluster my-cluster --instance-types t3.medium,t3.large")

if __name__ == "__main__":
    main()
