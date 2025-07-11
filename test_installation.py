#!/usr/bin/env python3
"""
Simple test script to verify k8s-helper installation
"""

def test_imports():
    """Test that all main components can be imported"""
    try:
        from k8s_helper import K8sClient
        print("✓ K8sClient imported successfully")
        
        from k8s_helper import K8sConfig
        print("✓ K8sConfig imported successfully")
        
        from k8s_helper.utils import format_pod_list
        print("✓ Utils imported successfully")
        
        from k8s_helper.config import get_config
        print("✓ Config functions imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without requiring a cluster"""
    try:
        from k8s_helper.utils import validate_name, validate_image, parse_env_vars
        
        # Test validation functions
        assert validate_name("test-app") == True
        assert validate_name("Test-App") == False
        assert validate_image("nginx:latest") == True
        assert validate_image("") == False
        
        # Test parsing functions
        env_vars = parse_env_vars("KEY1=value1,KEY2=value2")
        assert env_vars == {"KEY1": "value1", "KEY2": "value2"}
        
        print("✓ Basic utility functions work correctly")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_config():
    """Test configuration management"""
    try:
        from k8s_helper.config import K8sConfig
        
        config = K8sConfig()
        original_ns = config.get_namespace()
        
        # Test setting and getting values
        config.set_namespace("test-namespace")
        assert config.get_namespace() == "test-namespace"
        
        # Restore original
        config.set_namespace(original_ns)
        
        print("✓ Configuration management works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    print("Testing k8s-helper installation...")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Configuration Test", test_config)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            failed += 1
    
    print(f"\n" + "=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! k8s-helper is working correctly.")
        print("\nYou can now use k8s-helper:")
        print("  # Python API")
        print("  from k8s_helper import K8sClient")
        print("  client = K8sClient()")
        print("  # CLI")
        print("  k8s-helper --help")
    else:
        print(f"❌ {failed} test(s) failed. Please check the installation.")

if __name__ == "__main__":
    main()
