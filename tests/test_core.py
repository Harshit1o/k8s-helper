"""
Tests for k8s-helper core functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from kubernetes.client.rest import ApiException

from k8s_helper.core import K8sClient
from k8s_helper.utils import (
    format_age, 
    validate_name, 
    validate_namespace, 
    validate_image,
    parse_env_vars,
    parse_labels,
    format_pod_list,
    format_deployment_list,
    format_service_list
)


class TestK8sClient:
    """Test cases for K8sClient class"""
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_init_default(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test K8sClient initialization with default namespace"""
        client = K8sClient()
        
        assert client.namespace == "default"
        mock_load_config.assert_called_once()
        mock_apps_v1.assert_called_once()
        mock_core_v1.assert_called_once()
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_init_custom_namespace(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test K8sClient initialization with custom namespace"""
        client = K8sClient(namespace="test-namespace")
        
        assert client.namespace == "test-namespace"
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.config.load_incluster_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_init_fallback_to_incluster(self, mock_core_v1, mock_apps_v1, mock_incluster, mock_load_config):
        """Test K8sClient falls back to in-cluster config when kube config fails"""
        mock_load_config.side_effect = Exception("No kube config")
        
        client = K8sClient()
        
        mock_load_config.assert_called_once()
        mock_incluster.assert_called_once()
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_create_deployment_success(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test successful deployment creation"""
        mock_apps_v1_instance = Mock()
        mock_apps_v1.return_value = mock_apps_v1_instance
        mock_response = Mock()
        mock_apps_v1_instance.create_namespaced_deployment.return_value = mock_response
        
        client = K8sClient()
        result = client.create_deployment("test-app", "nginx:latest", replicas=2)
        
        assert result == mock_response
        mock_apps_v1_instance.create_namespaced_deployment.assert_called_once()
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_create_deployment_api_exception(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test deployment creation with API exception"""
        mock_apps_v1_instance = Mock()
        mock_apps_v1.return_value = mock_apps_v1_instance
        mock_apps_v1_instance.create_namespaced_deployment.side_effect = ApiException("API Error")
        
        client = K8sClient()
        result = client.create_deployment("test-app", "nginx:latest")
        
        assert result is None
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_delete_deployment_success(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test successful deployment deletion"""
        mock_apps_v1_instance = Mock()
        mock_apps_v1.return_value = mock_apps_v1_instance
        
        client = K8sClient()
        result = client.delete_deployment("test-app")
        
        assert result is True
        mock_apps_v1_instance.delete_namespaced_deployment.assert_called_once_with(
            name="test-app",
            namespace="default"
        )
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_scale_deployment_success(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test successful deployment scaling"""
        mock_apps_v1_instance = Mock()
        mock_apps_v1.return_value = mock_apps_v1_instance
        
        # Mock the read deployment response
        mock_deployment = Mock()
        mock_deployment.spec.replicas = 1
        mock_apps_v1_instance.read_namespaced_deployment.return_value = mock_deployment
        
        client = K8sClient()
        result = client.scale_deployment("test-app", 3)
        
        assert result is True
        assert mock_deployment.spec.replicas == 3
        mock_apps_v1_instance.patch_namespaced_deployment.assert_called_once()
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_create_pod_success(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test successful pod creation"""
        mock_core_v1_instance = Mock()
        mock_core_v1.return_value = mock_core_v1_instance
        mock_response = Mock()
        mock_core_v1_instance.create_namespaced_pod.return_value = mock_response
        
        client = K8sClient()
        result = client.create_pod("test-pod", "nginx:latest")
        
        assert result == mock_response
        mock_core_v1_instance.create_namespaced_pod.assert_called_once()
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_get_logs_success(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test successful log retrieval"""
        mock_core_v1_instance = Mock()
        mock_core_v1.return_value = mock_core_v1_instance
        mock_logs = "Test log output"
        mock_core_v1_instance.read_namespaced_pod_log.return_value = mock_logs
        
        client = K8sClient()
        result = client.get_logs("test-pod")
        
        assert result == mock_logs
        mock_core_v1_instance.read_namespaced_pod_log.assert_called_once()
    
    @patch('k8s_helper.core.config.load_kube_config')
    @patch('k8s_helper.core.client.AppsV1Api')
    @patch('k8s_helper.core.client.CoreV1Api')
    def test_create_service_success(self, mock_core_v1, mock_apps_v1, mock_load_config):
        """Test successful service creation"""
        mock_core_v1_instance = Mock()
        mock_core_v1.return_value = mock_core_v1_instance
        mock_response = Mock()
        mock_core_v1_instance.create_namespaced_service.return_value = mock_response
        
        client = K8sClient()
        result = client.create_service("test-service", port=80, target_port=8080)
        
        assert result == mock_response
        mock_core_v1_instance.create_namespaced_service.assert_called_once()


class TestUtils:
    """Test cases for utility functions"""
    
    def test_validate_name_valid(self):
        """Test name validation with valid names"""
        assert validate_name("test-app") is True
        assert validate_name("myapp123") is True
        assert validate_name("a") is True
        assert validate_name("app-123-test") is True
    
    def test_validate_name_invalid(self):
        """Test name validation with invalid names"""
        assert validate_name("Test-App") is False  # Uppercase
        assert validate_name("test_app") is False  # Underscore
        assert validate_name("-test") is False     # Starts with hyphen
        assert validate_name("test-") is False     # Ends with hyphen
        assert validate_name("") is False          # Empty
        assert validate_name("a" * 64) is False   # Too long
    
    def test_validate_namespace_valid(self):
        """Test namespace validation with valid names"""
        assert validate_namespace("default") is True
        assert validate_namespace("kube-system") is True
        assert validate_namespace("test-ns") is True
    
    def test_validate_image_valid(self):
        """Test image validation with valid names"""
        assert validate_image("nginx") is True
        assert validate_image("nginx:latest") is True
        assert validate_image("registry.io/nginx:v1.0") is True
    
    def test_validate_image_invalid(self):
        """Test image validation with invalid names"""
        assert validate_image("") is False
        assert validate_image("nginx with spaces") is False
    
    def test_parse_env_vars(self):
        """Test environment variable parsing"""
        result = parse_env_vars("KEY1=value1,KEY2=value2")
        expected = {"KEY1": "value1", "KEY2": "value2"}
        assert result == expected
    
    def test_parse_env_vars_empty(self):
        """Test environment variable parsing with empty string"""
        result = parse_env_vars("")
        assert result == {}
    
    def test_parse_env_vars_no_equals(self):
        """Test environment variable parsing with malformed input"""
        result = parse_env_vars("KEY1=value1,KEY2")
        expected = {"KEY1": "value1"}
        assert result == expected
    
    def test_parse_labels(self):
        """Test label parsing"""
        result = parse_labels("app=myapp,version=v1.0")
        expected = {"app": "myapp", "version": "v1.0"}
        assert result == expected
    
    def test_format_pod_list_empty(self):
        """Test pod list formatting with empty list"""
        result = format_pod_list([])
        assert result == "No pods found"
    
    def test_format_pod_list_with_pods(self):
        """Test pod list formatting with pods"""
        from datetime import datetime, timezone
        
        pods = [
            {
                'name': 'test-pod-1',
                'ready': True,
                'phase': 'Running',
                'restarts': 0,
                'age': datetime.now(timezone.utc),
                'node': 'node-1'
            }
        ]
        
        result = format_pod_list(pods)
        assert 'test-pod-1' in result
        assert 'Running' in result
        assert 'node-1' in result
    
    def test_format_deployment_list_empty(self):
        """Test deployment list formatting with empty list"""
        result = format_deployment_list([])
        assert result == "No deployments found"
    
    def test_format_service_list_empty(self):
        """Test service list formatting with empty list"""
        result = format_service_list([])
        assert result == "No services found"


class TestQuickFunctions:
    """Test cases for quick convenience functions"""
    
    @patch('k8s_helper.K8sClient')
    def test_quick_deployment(self, mock_client_class):
        """Test quick deployment creation"""
        from k8s_helper import quick_deployment
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_deployment.return_value = Mock()
        
        result = quick_deployment("test-app", "nginx:latest")
        
        assert result is True
        mock_client_class.assert_called_once_with(namespace="default")
        mock_client.create_deployment.assert_called_once_with("test-app", "nginx:latest", 1)
    
    @patch('k8s_helper.K8sClient')
    def test_quick_service(self, mock_client_class):
        """Test quick service creation"""
        from k8s_helper import quick_service
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_service.return_value = Mock()
        
        result = quick_service("test-service", 80)
        
        assert result is True
        mock_client_class.assert_called_once_with(namespace="default")
        mock_client.create_service.assert_called_once_with("test-service", 80, 80)
    
    @patch('k8s_helper.K8sClient')
    def test_quick_scale(self, mock_client_class):
        """Test quick deployment scaling"""
        from k8s_helper import quick_scale
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.scale_deployment.return_value = True
        
        result = quick_scale("test-app", 3)
        
        assert result is True
        mock_client_class.assert_called_once_with(namespace="default")
        mock_client.scale_deployment.assert_called_once_with("test-app", 3)


if __name__ == "__main__":
    pytest.main([__file__])
