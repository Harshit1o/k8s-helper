#!/usr/bin/env python3
"""
Development setup script for k8s-helper
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[*] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[+] {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("[*] Checking Python version...")
    if sys.version_info < (3, 8):
        print("[-] Python 3.8+ is required")
        return False
    print(f"[+] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible")
    return True

def check_kubernetes_access():
    """Check if kubectl is available and configured"""
    print("[*] Checking Kubernetes access...")
    try:
        result = subprocess.run("kubectl version --client", shell=True, check=True, capture_output=True, text=True)
        print("[+] kubectl is available")
        
        # Try to access cluster
        result = subprocess.run("kubectl cluster-info", shell=True, check=True, capture_output=True, text=True)
        print("[+] Kubernetes cluster is accessible")
        return True
    except subprocess.CalledProcessError:
        print("[!] kubectl not found or cluster not accessible")
        print("   Make sure kubectl is installed and configured")
        return False

def install_package():
    """Install the package in development mode"""
    print("[*] Installing k8s-helper in development mode...")
    
    # First install build dependencies
    if not run_command("pip install --upgrade pip setuptools wheel", "Upgrading pip and tools"):
        return False
    
    # Install in development mode with dev dependencies
    if not run_command("pip install -e .[dev]", "Installing k8s-helper with dev dependencies"):
        return False
    
    return True

def run_tests():
    """Run basic tests to verify installation"""
    print("[*] Running basic tests...")
    
    # Check if we can import the package
    try:
        import k8s_helper
        print("[+] k8s-helper package imported successfully")
    except ImportError as e:
        print(f"[-] Failed to import k8s-helper: {e}")
        return False
    
    # Run pytest if available
    try:
        subprocess.run("pytest tests/test_core.py -v", shell=True, check=True)
        print("[+] Tests passed")
    except subprocess.CalledProcessError:
        print("[!] Some tests failed (this might be expected without a Kubernetes cluster)")
    except FileNotFoundError:
        print("[!] pytest not found, skipping tests")
    
    return True

def show_usage_examples():
    """Show usage examples"""
    print("\n[*] k8s-helper is ready to use!")
    print("\nQuick examples:")
    print("  # Python API")
    print("  from k8s_helper import K8sClient")
    print("  client = K8sClient()")
    print("  client.create_deployment('my-app', 'nginx:latest')")
    print("")
    print("  # Command line")
    print("  k8s-helper create-deployment my-app nginx:latest")
    print("  k8s-helper list-pods")
    print("  k8s-helper logs my-pod")
    print("")
    print("  # Examples")
    print("  python examples/basic_web_app.py")
    print("  python examples/multi_tier_app.py")
    print("")
    print("[*] Check README.md for full documentation")

def main():
    """Main setup function"""
    print("[*] Setting up k8s-helper development environment")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("[-] Please run this script from the k8s-helper project root directory")
        sys.exit(1)
    
    # Check Kubernetes access (optional)
    check_kubernetes_access()
    
    # Install package
    if not install_package():
        print("[-] Installation failed")
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n[+] Setup completed successfully!")
    print("You can now use k8s-helper for your Kubernetes operations.")

if __name__ == "__main__":
    main()
