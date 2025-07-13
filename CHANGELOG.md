# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--version` option to CLI to show installed version
- Initial release of k8s-helper
- Complete Kubernetes resource management
- CLI interface with rich output
- Comprehensive documentation and examples

### Fixed
- Version consistency between `__init__.py` and `pyproject.toml`

## [0.1.0] - 2025-01-11

### Added
- **Core Features**
  - K8sClient class for Kubernetes operations
  - Pod management (create, delete, list, describe)
  - Deployment management (create, delete, scale, list, describe)
  - Service management (create, delete, list, describe)
  - Log retrieval with filtering options
  - Event monitoring and filtering
  - Resource description with detailed information

- **Configuration Management**
  - K8sConfig class for settings management
  - Environment variable overrides
  - Configuration file support (~/.k8s-helper/config.yaml)
  - Context management for different clusters

- **Utility Functions**
  - Resource validation (names, images, namespaces)
  - Output formatting (table, YAML, JSON)
  - Environment variable and label parsing
  - Age formatting for timestamps
  - YAML and JSON manifest generation

- **Command Line Interface**
  - Full CLI with typer and rich
  - All core operations available via CLI
  - Beautiful table output with colors
  - Interactive configuration management
  - Comprehensive help and documentation

- **Quick Functions**
  - Convenience functions for common operations
  - One-line deployment creation
  - Quick service setup
  - Easy scaling operations
  - Simple cleanup functions

- **Error Handling**
  - Comprehensive error handling throughout
  - Meaningful error messages
  - Graceful fallback for failed operations
  - Validation of inputs before API calls

- **Output Formats**
  - Table format for list operations
  - YAML format for detailed output
  - JSON format for programmatic use
  - Formatted logs and events
  - Status indicators with emojis

- **Development Tools**
  - Complete test suite with pytest
  - Integration tests for real cluster testing
  - Code formatting with black
  - Linting with flake8
  - Type checking with mypy
  - Coverage reporting

- **Documentation**
  - Comprehensive README with examples
  - API documentation
  - Usage examples for all features
  - Development setup guide
  - Contributing guidelines

- **Examples**
  - Basic web application deployment
  - Multi-tier application setup
  - Cleanup and maintenance scripts
  - Real-world usage scenarios

- **CI/CD**
  - GitHub Actions workflow
  - Multi-version Python testing
  - Security scanning with bandit and safety
  - Integration testing with kind
  - Automated PyPI publishing

### Dependencies
- kubernetes>=26.1.0 - Kubernetes Python client
- typer>=0.9.0 - CLI framework
- rich>=13.0.0 - Terminal output formatting
- pyyaml>=6.0 - YAML processing

### Development Dependencies
- pytest>=7.0.0 - Testing framework
- pytest-mock>=3.10.0 - Mock testing
- pytest-cov>=4.0.0 - Coverage reporting
- black>=22.0.0 - Code formatting
- flake8>=4.0.0 - Linting
- mypy>=0.991 - Type checking

### Installation
```bash
pip install k8s-helper
```

### Quick Start
```python
from k8s_helper import K8sClient

client = K8sClient()
client.create_deployment("my-app", "nginx:latest", replicas=3)
client.create_service("my-app-service", port=80, target_port=80)
```

### CLI Usage
```bash
k8s-helper create-deployment my-app nginx:latest --replicas 3
k8s-helper create-service my-app-service 80 --target-port 80
k8s-helper list-pods
k8s-helper logs my-pod
```

### Features Overview
- ✅ Pod Management - Create, delete, list, describe pods
- ✅ Deployment Management - Full deployment lifecycle
- ✅ Service Management - Service creation and management
- ✅ Scaling - Easy deployment scaling
- ✅ Logs - Pod log retrieval with filtering
- ✅ Events - Event monitoring and filtering
- ✅ Resource Description - Detailed resource information
- ✅ Configuration - Flexible configuration management
- ✅ CLI Interface - Full command-line interface
- ✅ Output Formats - Table, YAML, JSON output
- ✅ Error Handling - Comprehensive error management
- ✅ Validation - Input validation and sanitization
- ✅ Documentation - Complete documentation and examples

### Breaking Changes
- None (initial release)

### Security
- Input validation for all parameters
- Secure defaults for all operations
- No hardcoded credentials or secrets
- Follows Kubernetes security best practices

### Performance
- Efficient API calls with minimal overhead
- Caching of client connections
- Optimized resource listing and filtering
- Lazy loading of optional dependencies

### Known Issues
- None reported

### Future Plans
- Support for more Kubernetes resources (ConfigMaps, Secrets, etc.)
- Advanced deployment strategies (rolling updates, canary deployments)
- Resource monitoring and alerting
- Integration with popular CI/CD tools
- Plugin system for custom operations
- Web UI for visual management
- Multi-cluster support
- Advanced security features

### Contributors
- Harshit Chatterjee (@Harshit1o) - Initial development

### License
MIT License - see LICENSE file for details.

---

## Migration Guide

### From kubectl to k8s-helper

Common kubectl commands and their k8s-helper equivalents:

```bash
# kubectl create deployment
kubectl create deployment my-app --image=nginx:latest --replicas=3
# k8s-helper
k8s-helper create-deployment my-app nginx:latest --replicas 3

# kubectl expose deployment
kubectl expose deployment my-app --port=80 --target-port=80
# k8s-helper
k8s-helper create-service my-app-service 80 --target-port 80

# kubectl get pods
kubectl get pods
# k8s-helper
k8s-helper list-pods

# kubectl logs
kubectl logs my-pod
# k8s-helper
k8s-helper logs my-pod

# kubectl describe
kubectl describe pod my-pod
# k8s-helper
k8s-helper describe pod my-pod

# kubectl scale
kubectl scale deployment my-app --replicas=5
# k8s-helper
k8s-helper scale-deployment my-app 5
```

### From Kubernetes Python Client to k8s-helper

```python
# Before (kubernetes python client)
from kubernetes import client, config
config.load_kube_config()
apps_v1 = client.AppsV1Api()

deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name="my-app"),
    spec=client.V1DeploymentSpec(
        replicas=3,
        selector=client.V1LabelSelector(
            match_labels={"app": "my-app"}
        ),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "my-app"}),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="my-app",
                        image="nginx:latest",
                        ports=[client.V1ContainerPort(container_port=80)]
                    )
                ]
            )
        )
    )
)

apps_v1.create_namespaced_deployment(
    body=deployment,
    namespace="default"
)

# After (k8s-helper)
from k8s_helper import K8sClient

client = K8sClient()
client.create_deployment("my-app", "nginx:latest", replicas=3)
```
