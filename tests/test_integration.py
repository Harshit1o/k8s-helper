#!/usr/bin/env python3
"""
Integration test for k8s-helper
This script tests the library against a real Kubernetes cluster
"""

import sys
import time
from k8s_helper import K8sClient, format_deployment_list, format_service_list, format_pod_list

def test_basic_operations():
    """Test basic CRUD operations"""
    print("🧪 Testing basic operations...")
    
    # Initialize client with test namespace
    client = K8sClient(namespace="k8s-helper-test")
    
    test_name = "test-app"
    
    print(f"  Creating deployment: {test_name}")
    deployment = client.create_deployment(
        name=test_name,
        image="nginx:alpine",
        replicas=1,
        container_port=80,
        labels={"test": "k8s-helper"}
    )
    
    if not deployment:
        print("❌ Failed to create deployment")
        return False
    
    print(f"  Creating service: {test_name}-service")
    service = client.create_service(
        name=f"{test_name}-service",
        port=80,
        target_port=80,
        selector={"test": "k8s-helper"}
    )
    
    if not service:
        print("❌ Failed to create service")
        return False
    
    print("  Waiting for deployment to be ready...")
    if not client.wait_for_deployment_ready(test_name, timeout=120):
        print("❌ Deployment did not become ready")
        return False
    
    print("  Testing list operations...")
    deployments = client.list_deployments()
    services = client.list_services()
    pods = client.list_pods()
    
    if not deployments or not services or not pods:
        print("❌ List operations failed")
        return False
    
    print("  Testing describe operations...")
    pod_name = pods[0]['name']
    pod_info = client.describe_pod(pod_name)
    deployment_info = client.describe_deployment(test_name)
    service_info = client.describe_service(f"{test_name}-service")
    
    if not pod_info or not deployment_info or not service_info:
        print("❌ Describe operations failed")
        return False
    
    print("  Testing logs...")
    logs = client.get_logs(pod_name)
    if logs is None:
        print("❌ Log retrieval failed")
        return False
    
    print("  Testing events...")
    events = client.get_events()
    if events is None:
        print("❌ Event retrieval failed")
        return False
    
    print("  Testing scaling...")
    if not client.scale_deployment(test_name, 2):
        print("❌ Scaling failed")
        return False
    
    # Wait a bit for scaling
    time.sleep(10)
    
    print("  Cleaning up...")
    if not client.delete_deployment(test_name):
        print("❌ Failed to delete deployment")
        return False
    
    if not client.delete_service(f"{test_name}-service"):
        print("❌ Failed to delete service")
        return False
    
    print("✅ Basic operations test passed")
    return True

def test_error_handling():
    """Test error handling"""
    print("🧪 Testing error handling...")
    
    client = K8sClient(namespace="k8s-helper-test")
    
    # Test with invalid names
    print("  Testing invalid resource names...")
    result = client.create_deployment("Invalid-Name", "nginx:latest")
    if result is not None:
        print("❌ Should have failed with invalid name")
        return False
    
    # Test deleting non-existent resources
    print("  Testing deletion of non-existent resources...")
    result = client.delete_deployment("non-existent-deployment")
    if result is True:
        print("❌ Should have failed deleting non-existent resource")
        return False
    
    print("✅ Error handling test passed")
    return True

def test_formatting():
    """Test output formatting"""
    print("🧪 Testing output formatting...")
    
    # Test with empty data
    empty_pods = format_pod_list([])
    empty_deployments = format_deployment_list([])
    empty_services = format_service_list([])
    
    if "No pods found" not in empty_pods:
        print("❌ Empty pods formatting failed")
        return False
    
    if "No deployments found" not in empty_deployments:
        print("❌ Empty deployments formatting failed")
        return False
    
    if "No services found" not in empty_services:
        print("❌ Empty services formatting failed")
        return False
    
    print("✅ Formatting test passed")
    return True

def test_configuration():
    """Test configuration management"""
    print("🧪 Testing configuration...")
    
    from k8s_helper.config import K8sConfig
    
    config = K8sConfig()
    
    # Test basic configuration
    original_namespace = config.get_namespace()
    config.set_namespace("test-namespace")
    
    if config.get_namespace() != "test-namespace":
        print("❌ Configuration set/get failed")
        return False
    
    # Restore original
    config.set_namespace(original_namespace)
    
    print("✅ Configuration test passed")
    return True

def main():
    """Run all tests"""
    print("🧪 Running k8s-helper integration tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Formatting", test_formatting),
        ("Error Handling", test_error_handling),
        ("Basic Operations", test_basic_operations),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print(f"\n📊 Test Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
