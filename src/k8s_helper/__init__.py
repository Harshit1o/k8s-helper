"""
k8s-helper: A simplified Python wrapper for common Kubernetes operations
"""

from .core import K8sClient
from .config import K8sConfig, get_config
from .utils import (
    format_pod_list,
    format_deployment_list,
    format_service_list,
    format_events,
    format_age,
    validate_name,
    validate_namespace,
    validate_image,
    parse_env_vars,
    parse_labels,
    print_status,
    create_deployment_manifest,
    create_service_manifest
)

__version__ = "0.2.7"
__author__ = "Harshit Chatterjee"
__email__ = "harshitchatterjee50@gmail.com"

# Convenience functions for quick operations
def quick_deployment(name: str, image: str, replicas: int = 1, namespace: str = "default") -> bool:
    """Quickly create a deployment"""
    client = K8sClient(namespace=namespace)
    result = client.create_deployment(name, image, replicas)
    return result is not None

def quick_service(name: str, port: int, target_port: int = None, namespace: str = "default") -> bool:
    """Quickly create a service"""
    if target_port is None:
        target_port = port
    
    client = K8sClient(namespace=namespace)
    result = client.create_service(name, port, target_port)
    return result is not None

def quick_scale(deployment_name: str, replicas: int, namespace: str = "default") -> bool:
    """Quickly scale a deployment"""
    client = K8sClient(namespace=namespace)
    return client.scale_deployment(deployment_name, replicas)

def quick_logs(pod_name: str, namespace: str = "default") -> str:
    """Quickly get pod logs"""
    client = K8sClient(namespace=namespace)
    return client.get_logs(pod_name)

def quick_delete_deployment(name: str, namespace: str = "default") -> bool:
    """Quickly delete a deployment"""
    client = K8sClient(namespace=namespace)
    return client.delete_deployment(name)

def quick_delete_service(name: str, namespace: str = "default") -> bool:
    """Quickly delete a service"""
    client = K8sClient(namespace=namespace)
    return client.delete_service(name)

# Export main classes and functions
__all__ = [
    'K8sClient',
    'K8sConfig',
    'get_config',
    'format_pod_list',
    'format_deployment_list',
    'format_service_list',
    'format_events',
    'format_age',
    'validate_name',
    'validate_namespace',
    'validate_image',
    'parse_env_vars',
    'parse_labels',
    'print_status',
    'create_deployment_manifest',
    'create_service_manifest',
    'quick_deployment',
    'quick_service',
    'quick_scale',
    'quick_logs',
    'quick_delete_deployment',
    'quick_delete_service'
]
