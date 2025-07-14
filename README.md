# k8s-helper

A simplified Python wrapper for common Kubernetes operations that makes it easy to manage pods, deployments, services, and more.

## Features

- ✅ **Pod Management**: Create, delete, and list pods
- ✅ **Deployment Management**: Create, delete, scale, and list deployments with init containers
- ✅ **Service Management**: Create, delete, list services with URL retrieval
- ✅ **AWS EKS Integration**: Create and manage EKS clusters with automatic configuration
- ✅ **Secrets Management**: Create, list, and delete Kubernetes secrets
- ✅ **Persistent Volume Claims**: Create, list, and delete PVCs with multiple access modes
- ✅ **Service URL Discovery**: Get service URLs including AWS ELB DNS names
- ✅ **Advanced Deployments**: Support for init containers, volume mounts, and complex configurations
- ✅ **Resource Monitoring**: Get logs, events, and resource descriptions
- ✅ **Easy Configuration**: Simple configuration management
- ✅ **Formatted Output**: Beautiful table, YAML, and JSON output formats
- ✅ **Error Handling**: Comprehensive error handling with helpful messages
- ✅ **Quick Functions**: Convenience functions for common tasks

## Installation

```bash
pip install k8s-helper-cli
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

**Important**: k8s-helper requires an active Kubernetes cluster connection. Without a properly configured kubectl and accessible cluster, the commands will fail with configuration errors.

### AWS EKS Features Prerequisites

For AWS EKS integration features:
- AWS CLI configured with appropriate credentials (`aws configure`)
- AWS IAM permissions for EKS, EC2, and IAM operations
- boto3 package (automatically installed with k8s-helper-cli)

### Setting up Kubernetes (Choose one):

1. **Local Development**: 
   - [minikube](https://minikube.sigs.k8s.io/docs/start/)
   - [kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
   - [Docker Desktop](https://docs.docker.com/desktop/kubernetes/) (Enable Kubernetes)

2. **Cloud Providers**:
   - [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine)
   - [Amazon Elastic Kubernetes Service (EKS)](https://aws.amazon.com/eks/)
   - [Azure Kubernetes Service (AKS)](https://azure.microsoft.com/en-us/services/kubernetes-service/)

3. **Verify Setup**:
   ```bash
   # Check if kubectl is configured
   kubectl cluster-info
   
   # List nodes to verify cluster access
   kubectl get nodes
   ```

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

## CLI Usage

k8s-helper provides a command-line interface for Kubernetes operations. After installation, you can use the `k8s-helper` command directly in your terminal.

### Available Commands

```bash
# Show help
k8s-helper --help

# Show version
k8s-helper --version

# Configure settings
k8s-helper config --namespace my-namespace
k8s-helper config --output-format yaml
k8s-helper config --timeout 300
k8s-helper config --show  # Show current configuration
```

### Pod Management

```bash
# Create a pod
k8s-helper create-pod my-pod nginx:latest --namespace my-namespace

# Delete a pod
k8s-helper delete-pod my-pod --namespace my-namespace

# List pods
k8s-helper list-pods --namespace my-namespace
k8s-helper list-pods --output yaml

# Get pod logs
k8s-helper logs my-pod --namespace my-namespace
```

### Deployment Management

```bash
# Create a deployment
k8s-helper create-deployment my-app nginx:latest --replicas 3 --namespace my-namespace

# Scale a deployment
k8s-helper scale-deployment my-app --replicas 5 --namespace my-namespace

# Delete a deployment
k8s-helper delete-deployment my-app --namespace my-namespace

# List deployments
k8s-helper list-deployments --namespace my-namespace
k8s-helper list-deployments --output yaml
```

### Service Management

```bash
# Create a service
k8s-helper create-service my-service --port 80 --target-port 8080 --type ClusterIP --namespace my-namespace

# Delete a service
k8s-helper delete-service my-service --namespace my-namespace

# List services
k8s-helper list-services --namespace my-namespace
k8s-helper list-services --output yaml
```

### Monitoring and Events

```bash
# Get events
k8s-helper events --namespace my-namespace

# Get namespace status
k8s-helper status --namespace my-namespace

# Describe resources
k8s-helper describe pod my-pod --namespace my-namespace
k8s-helper describe deployment my-app --namespace my-namespace
k8s-helper describe service my-service --namespace my-namespace
```

### Application Deployment

```bash
# Deploy a complete application (deployment + service)
k8s-helper apply my-app nginx:latest --replicas 3 --port 80 --service-type LoadBalancer --namespace my-namespace

# Clean up an application (delete deployment + service)
k8s-helper cleanup my-app --namespace my-namespace
```

### Basic Examples

#### Deploy a Web Application
```bash
# Deploy nginx with 3 replicas and LoadBalancer service
k8s-helper apply webapp nginx:latest --replicas 3 --port 80 --service-type LoadBalancer

# Check deployment status
k8s-helper list-deployments
k8s-helper list-services
k8s-helper status
```

#### Deploy a Database
```bash
# Deploy postgres
k8s-helper create-deployment postgres-db postgres:13 --replicas 1
k8s-helper create-service postgres-service --port 5432 --target-port 5432 --type ClusterIP

# Check logs
k8s-helper logs postgres-db
```

#### Scale Applications
```bash
# Scale web application
k8s-helper scale-deployment webapp --replicas 5

# Check scaling
k8s-helper list-deployments
```

#### Clean Up
```bash
# Clean up the web application
k8s-helper cleanup webapp

# Or delete components individually
k8s-helper delete-deployment postgres-db
k8s-helper delete-service postgres-service
```

### Configuration

```bash
# Set default namespace
k8s-helper config --namespace production

# Set output format
k8s-helper config --output-format yaml

# Show current configuration
k8s-helper config --show
```

### Output Formats

The CLI supports different output formats:

```bash
# Table format (default)
k8s-helper list-pods

# YAML format
k8s-helper list-pods --output yaml

# JSON format
k8s-helper list-pods --output json
```

### Environment Variables

```bash
# Set default namespace
export K8S_HELPER_NAMESPACE=my-namespace

# Set output format
export K8S_HELPER_OUTPUT_FORMAT=yaml

# Now all commands will use these defaults
k8s-helper list-pods
```

### Shell Completion

```bash
# Install completion for bash
k8s-helper --install-completion bash

# Install completion for zsh
k8s-helper --install-completion zsh

# Show completion script
k8s-helper --show-completion bash
```

### AWS EKS Integration

```bash
# Create an EKS cluster
k8s-helper create-eks-cluster my-cluster --region us-west-2 --version 1.29

# Create EKS cluster with custom settings
k8s-helper create-eks-cluster my-cluster \
  --region us-east-1 \
  --instance-types t3.medium,t3.large \
  --min-size 2 \
  --max-size 10 \
  --desired-size 3 \
  --node-group my-nodes \
  --wait

# Note: Requires AWS credentials configured (aws configure)
```

### Secrets Management

```bash
# Create a secret
k8s-helper create-secret my-secret --data "username=admin,password=secret123"

# Create a TLS secret
k8s-helper create-secret tls-secret --data "tls.crt=cert_content,tls.key=key_content" --type kubernetes.io/tls

# List secrets
k8s-helper list-secrets --namespace my-namespace

# Delete a secret
k8s-helper delete-secret my-secret --namespace my-namespace
```

### Persistent Volume Claims (PVC)

```bash
# Create a PVC
k8s-helper create-pvc my-storage 10Gi --access-modes ReadWriteOnce

# Create PVC with specific storage class
k8s-helper create-pvc my-storage 50Gi --storage-class fast-ssd --access-modes ReadWriteMany

# List PVCs
k8s-helper list-pvcs --namespace my-namespace

# Delete a PVC
k8s-helper delete-pvc my-storage --namespace my-namespace
```

### Service URL Retrieval

```bash
# Get service URL (including AWS ELB URLs)
k8s-helper service-url my-service --namespace my-namespace

# Watch for URL changes (useful for LoadBalancer provisioning)
k8s-helper service-url my-service --watch --namespace my-namespace

# Shows:
# - ClusterIP access information
# - NodePort URLs
# - AWS ELB DNS names for LoadBalancer services
# - External IPs and hostnames
```

### Enhanced Application Deployment

```bash
# Deploy with init container
k8s-helper apply my-app nginx:latest \
  --init-container "init-db:postgres:13:pg_isready -h db" \
  --init-env "PGHOST=db,PGPORT=5432"

# Deploy with PVC mount
k8s-helper apply my-app nginx:latest \
  --pvc "my-storage:/data" \
  --replicas 2

# Deploy with secret mount
k8s-helper apply my-app nginx:latest \
  --secret "my-secret:/etc/secrets" \
  --port 8080

# Deploy with LoadBalancer and show URL
k8s-helper apply my-app nginx:latest \
  --service-type LoadBalancer \
  --wait \
  --show-url

# Complex deployment with multiple features
k8s-helper apply my-app nginx:latest \
  --replicas 3 \
  --port 8080 \
  --service-type LoadBalancer \
  --env "ENV=production,DEBUG=false" \
  --labels "app=my-app,version=v1.0" \
  --init-container "migrate:migrate-tool:latest:migrate up" \
  --init-env "DB_HOST=postgres,DB_PORT=5432" \
  --secret "db-secret:/etc/db" \
  --pvc "app-storage:/var/data" \
  --wait \
  --show-url
```

## Real-World Examples

### 1. Simple Web Application

```bash
# Deploy a web application
k8s-helper apply webapp nginx:latest --replicas 3 --port 80 --service-type LoadBalancer

# Check deployment
k8s-helper list-deployments
k8s-helper list-services
k8s-helper status
```

### 2. Database Setup

```bash
# Deploy PostgreSQL database
k8s-helper create-deployment postgres-db postgres:13 --replicas 1
k8s-helper create-service postgres-service --port 5432 --target-port 5432 --type ClusterIP

# Check database
k8s-helper logs postgres-db
k8s-helper describe deployment postgres-db
```

### 3. Multi-Environment Deployment

```bash
# Production
k8s-helper config --namespace production
k8s-helper apply webapp myapp:v1.0.0 --replicas 5 --port 8080 --service-type LoadBalancer

# Staging
k8s-helper config --namespace staging
k8s-helper apply webapp myapp:v1.1.0-rc1 --replicas 2 --port 8080 --service-type ClusterIP

# Development
k8s-helper config --namespace development
k8s-helper apply webapp myapp:latest --replicas 1 --port 8080 --service-type NodePort
```

### 4. Application Scaling

```bash
# Scale up for high traffic
k8s-helper scale-deployment webapp --replicas 10

# Monitor scaling
k8s-helper list-deployments
k8s-helper events

# Scale down after traffic reduces
k8s-helper scale-deployment webapp --replicas 3
```

### 5. Debugging and Monitoring

```bash
# Get comprehensive status
k8s-helper status
k8s-helper list-deployments
k8s-helper list-pods
k8s-helper list-services

# Check logs
k8s-helper logs webapp

# Get events
k8s-helper events

# Describe resources
k8s-helper describe deployment webapp
k8s-helper describe service webapp-service
```

### 6. Clean Up

```bash
# Clean up complete application
k8s-helper cleanup webapp

# Or clean up individual components
k8s-helper delete-deployment postgres-db
k8s-helper delete-service postgres-service
```

## Best Practices

### 1. Resource Management
```bash
# Use appropriate replica counts for high availability
k8s-helper apply my-app nginx:latest --replicas 3

# Monitor resource usage
k8s-helper status
k8s-helper list-deployments
```

### 2. Environment Management
```bash
# Use different namespaces for different environments
k8s-helper config --namespace production
k8s-helper config --namespace staging  
k8s-helper config --namespace development
```

### 3. Service Types
```bash
# Use ClusterIP for internal services
k8s-helper create-service internal-api --port 8080 --type ClusterIP

# Use LoadBalancer for external access
k8s-helper create-service public-web --port 80 --type LoadBalancer
```

### 4. Monitoring and Debugging
```bash
# Regular health checks
k8s-helper status
k8s-helper events

# Log monitoring
k8s-helper logs my-app
```

### 5. Configuration Management
```bash
# Set sensible defaults
k8s-helper config --namespace my-app
k8s-helper config --output-format yaml
```

## Limitations

**Important**: k8s-helper requires an active Kubernetes cluster connection to function. The CLI and Python API will fail if:

- No kubectl configuration is found (`~/.kube/config`)
- No active Kubernetes cluster is available
- kubectl is not properly configured

### Current CLI Limitations:

- **Resource limits**: `--cpu-limit` and `--memory-limit` options are not implemented
- **Advanced logging**: `--tail`, `--follow`, `--container` options are not available
- **Advanced options**: Some documented options like `--env`, `--labels` may not be available in all commands
- **Batch operations**: Multiple resource operations in single commands are not supported
- **Advanced monitoring**: `--watch`, `--since`, `--all-namespaces` options are not implemented

### Error Handling:

If you see errors like:
```
ConfigException: Invalid kube-config file. No configuration found.
ConfigException: Service host/port is not set.
```

This means you need to:
1. Install and configure kubectl
2. Set up access to a Kubernetes cluster
3. Verify with `kubectl cluster-info`

The CLI provides core functionality for basic Kubernetes operations. For advanced features, use the Python API directly or kubectl.

## Troubleshooting

### Common Issues

#### 1. Kubernetes Configuration Errors

**Error**: `ConfigException: Invalid kube-config file. No configuration found.`

**Solution**:
```bash
# Check if kubectl is installed
kubectl version --client

# Check if kubectl is configured
kubectl cluster-info

# If not configured, set up a cluster (example with minikube)
minikube start
```

#### 2. Cluster Connection Issues

**Error**: `ConfigException: Service host/port is not set.`

**Solution**:
```bash
# Verify cluster is running
kubectl get nodes

# Check current context
kubectl config current-context

# Switch context if needed
kubectl config use-context <context-name>
```

#### 3. Namespace Issues

**Error**: `Namespace 'xyz' not found`

**Solution**:
```bash
# List all namespaces
kubectl get namespaces

# Create namespace if needed
kubectl create namespace <namespace-name>

# Or use default namespace
k8s-helper config --namespace default
```

#### 4. Permission Issues

**Error**: `Forbidden: User cannot list pods`

**Solution**:
```bash
# Check current user permissions
kubectl auth can-i list pods

# Check RBAC settings
kubectl get clusterrolebinding
```

### Testing Without a Cluster

If you want to test the package without a real Kubernetes cluster, you can:

1. **Use minikube** (recommended for development):
   ```bash
   # Install minikube
   # Windows: choco install minikube
   # macOS: brew install minikube
   # Linux: curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   
   # Start minikube
   minikube start
   
   # Test k8s-helper
   k8s-helper list-pods
   ```

2. **Use kind** (Kubernetes in Docker):
   ```bash
   # Install kind
   # Windows: choco install kind
   # macOS: brew install kind
   # Linux: curl -Lo kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
   
   # Create cluster
   kind create cluster
   
   # Test k8s-helper
   k8s-helper list-pods
   ```

3. **Use Docker Desktop** (if you have Docker Desktop):
   ```bash
   # Enable Kubernetes in Docker Desktop settings
   # Then test
   k8s-helper list-pods
   ```

### Getting Help

- **Documentation**: Check this README for usage examples
- **GitHub Issues**: [Report bugs or request features](https://github.com/Harshit1o/k8s-helper/issues)
- **Kubernetes Docs**: [Official Kubernetes documentation](https://kubernetes.io/docs/)
- **kubectl Reference**: [kubectl command reference](https://kubernetes.io/docs/reference/kubectl/)
