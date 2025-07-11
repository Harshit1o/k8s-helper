# k8s-helper

A simplified Python wrapper for common Kubernetes operations that makes it easy to manage pods, deployments, services, and more.

## Features

- ✅ **Pod Management**: Create, delete, and list pods
- ✅ **Deployment Management**: Create, delete, scale, and list deployments
- ✅ **Service Management**: Create, delete, and list services
- ✅ **Resource Monitoring**: Get logs, events, and resource descriptions
- ✅ **Easy Configuration**: Simple configuration management
- ✅ **Formatted Output**: Beautiful table, YAML, and JSON output formats
- ✅ **Error Handling**: Comprehensive error handling with helpful messages
- ✅ **Quick Functions**: Convenience functions for common tasks

## Installation

```bash
pip install k8s-helper
```

### Development Installation

```bash
git clone https://github.com/Harshit1o/k8s-helper.git
cd k8s-helper
pip install -e .
```

## Prerequisites

- Python 3.8+
- kubectl configured with access to a Kubernetes cluster
- Kubernetes cluster (local or remote)

## Quick Start

```python
from k8s_helper import K8sClient

# Initialize client with default namespace
client = K8sClient()

# Or specify a namespace
client = K8sClient(namespace="my-namespace")

# Create a deployment
client.create_deployment(
    name="my-app",
    image="nginx:latest",
    replicas=3,
    container_port=80
)

# Create a service
client.create_service(
    name="my-app-service",
    port=80,
    target_port=80,
    service_type="ClusterIP"
)

# Scale deployment
client.scale_deployment("my-app", replicas=5)

# Get logs
logs = client.get_logs("my-app-pod-12345")

# List resources
pods = client.list_pods()
deployments = client.list_deployments()
services = client.list_services()
```

## Detailed Usage

### Pod Management

```python
# Create a pod
client.create_pod(
    name="my-pod",
    image="nginx:latest",
    container_port=80,
    env_vars={"ENV": "production", "DEBUG": "false"},
    labels={"app": "my-app", "version": "v1.0"}
)

# Delete a pod
client.delete_pod("my-pod")

# List all pods
pods = client.list_pods()
print(format_pod_list(pods))

# Describe a pod
pod_info = client.describe_pod("my-pod")
```

### Deployment Management

```python
# Create a deployment with environment variables
client.create_deployment(
    name="my-app",
    image="nginx:latest",
    replicas=3,
    container_port=80,
    env_vars={"ENV": "production"},
    labels={"app": "my-app", "tier": "frontend"}
)

# Scale deployment
client.scale_deployment("my-app", replicas=5)

# Delete deployment
client.delete_deployment("my-app")

# List deployments
deployments = client.list_deployments()
print(format_deployment_list(deployments))

# Wait for deployment to be ready
client.wait_for_deployment_ready("my-app", timeout=300)
```

### Service Management

```python
# Create a ClusterIP service
client.create_service(
    name="my-app-service",
    port=80,
    target_port=8080,
    service_type="ClusterIP"
)

# Create a LoadBalancer service
client.create_service(
    name="my-app-lb",
    port=80,
    target_port=80,
    service_type="LoadBalancer",
    selector={"app": "my-app"}
)

# Delete service
client.delete_service("my-app-service")

# List services
services = client.list_services()
print(format_service_list(services))
```

### Logs and Events

```python
# Get pod logs
logs = client.get_logs("my-pod")

# Get logs with tail
logs = client.get_logs("my-pod", tail_lines=100)

# Get logs from specific container
logs = client.get_logs("my-pod", container_name="nginx")

# Get events
events = client.get_events()
print(format_events(events))

# Get events for specific resource
events = client.get_events("my-pod")
```

### Resource Description

```python
# Describe pod
pod_info = client.describe_pod("my-pod")
print(format_yaml_output(pod_info))

# Describe deployment
deployment_info = client.describe_deployment("my-app")
print(format_json_output(deployment_info))

# Describe service
service_info = client.describe_service("my-service")
```

## Quick Functions

For simple operations, use the convenience functions:

```python
from k8s_helper import (
    quick_deployment,
    quick_service,
    quick_scale,
    quick_logs,
    quick_delete_deployment,
    quick_delete_service
)

# Quick deployment
quick_deployment("my-app", "nginx:latest", replicas=3)

# Quick service
quick_service("my-service", port=80)

# Quick scaling
quick_scale("my-app", replicas=5)

# Quick logs
logs = quick_logs("my-pod")

# Quick cleanup
quick_delete_deployment("my-app")
quick_delete_service("my-service")
```

## Configuration

k8s-helper supports configuration through files and environment variables:

```python
from k8s_helper import get_config

# Get configuration
config = get_config()

# Set default namespace
config.set_namespace("my-namespace")

# Set output format
config.set_output_format("yaml")  # table, yaml, json

# Set timeout
config.set_timeout(600)

# Save configuration
config.save_config()
```

### Environment Variables

- `K8S_HELPER_NAMESPACE`: Default namespace
- `K8S_HELPER_OUTPUT_FORMAT`: Output format (table, yaml, json)
- `K8S_HELPER_TIMEOUT`: Default timeout in seconds
- `K8S_HELPER_VERBOSE`: Enable verbose output (true/false)
- `KUBECONFIG`: Path to kubectl config file

## Output Formatting

The library provides several output formats:

```python
from k8s_helper.utils import (
    format_pod_list,
    format_deployment_list,
    format_service_list,
    format_events,
    format_yaml_output,
    format_json_output
)

# Format as table
pods = client.list_pods()
print(format_pod_list(pods))

# Format as YAML
pod_info = client.describe_pod("my-pod")
print(format_yaml_output(pod_info))

# Format as JSON
deployment_info = client.describe_deployment("my-app")
print(format_json_output(deployment_info))
```

## Error Handling

The library provides comprehensive error handling:

```python
# All operations return None/False on failure
result = client.create_deployment("my-app", "nginx:latest")
if result is None:
    print("Failed to create deployment")

# Boolean operations return True/False
success = client.delete_deployment("my-app")
if not success:
    print("Failed to delete deployment")

# Use try-except for custom error handling
try:
    client.create_deployment("my-app", "nginx:latest")
except Exception as e:
    print(f"Error: {e}")
```

## Advanced Usage

### Using YAML Manifests

```python
from k8s_helper.utils import create_deployment_manifest, create_service_manifest

# Create deployment manifest
deployment_manifest = create_deployment_manifest(
    name="my-app",
    image="nginx:latest",
    replicas=3,
    port=80,
    env_vars={"ENV": "production"},
    labels={"app": "my-app"}
)

# Create service manifest
service_manifest = create_service_manifest(
    name="my-app-service",
    port=80,
    target_port=80,
    service_type="ClusterIP",
    selector={"app": "my-app"}
)

print(format_yaml_output(deployment_manifest))
```

### Working with Multiple Namespaces

```python
# Create clients for different namespaces
prod_client = K8sClient(namespace="production")
dev_client = K8sClient(namespace="development")

# Deploy to production
prod_client.create_deployment("my-app", "nginx:1.20", replicas=5)

# Deploy to development
dev_client.create_deployment("my-app", "nginx:latest", replicas=1)
```

### Monitoring and Health Checks

```python
# Check namespace resources
resources = client.get_namespace_resources()
print(f"Pods: {resources['pods']}")
print(f"Deployments: {resources['deployments']}")
print(f"Services: {resources['services']}")

# Wait for deployment to be ready
if client.wait_for_deployment_ready("my-app", timeout=300):
    print("Deployment is ready!")
else:
    print("Deployment failed to become ready")
```

## Examples

### Complete Application Deployment

```python
from k8s_helper import K8sClient

# Initialize client
client = K8sClient(namespace="my-app")

# Create deployment
client.create_deployment(
    name="web-app",
    image="nginx:latest",
    replicas=3,
    container_port=80,
    env_vars={"ENV": "production"},
    labels={"app": "web-app", "tier": "frontend"}
)

# Create service
client.create_service(
    name="web-app-service",
    port=80,
    target_port=80,
    service_type="LoadBalancer",
    selector={"app": "web-app"}
)

# Wait for deployment to be ready
if client.wait_for_deployment_ready("web-app"):
    print("✅ Application deployed successfully!")
    
    # Show status
    print("\nDeployments:")
    print(format_deployment_list(client.list_deployments()))
    
    print("\nServices:")
    print(format_service_list(client.list_services()))
    
    print("\nPods:")
    print(format_pod_list(client.list_pods()))
else:
    print("❌ Deployment failed!")
```

### Cleanup Script

```python
from k8s_helper import K8sClient

client = K8sClient(namespace="my-app")

# Clean up resources
resources_to_clean = [
    "web-app",
    "database",
    "cache"
]

for resource in resources_to_clean:
    print(f"Cleaning up {resource}...")
    client.delete_deployment(resource)
    client.delete_service(f"{resource}-service")

print("✅ Cleanup completed!")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Testing

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=k8s_helper tests/
```

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/Harshit1o/k8s-helper/issues)
- Documentation: [Full documentation](https://github.com/Harshit1o/k8s-helper)

## Changelog

### v0.1.0
- Initial release
- Basic pod, deployment, and service management
- Configuration management
- Comprehensive error handling
- Multiple output formats
- Quick convenience functions
