# k8s-helper v0.2.4 - Node Group Support

## What's New

### Automatic Node Group Creation
- EKS clusters now automatically create managed node groups by default
- No more empty clusters with no worker nodes
- Supports both ON_DEMAND and SPOT capacity types

### New CLI Commands

#### Enhanced create-eks-cluster
```bash
# Create cluster with automatic node group (default)
k8s-helper create-eks-cluster my-cluster

# Create cluster without node group
k8s-helper create-eks-cluster my-cluster --no-nodegroup

# Create with SPOT instances
k8s-helper create-eks-cluster my-cluster --capacity-type SPOT

# Create with multiple instance types
k8s-helper create-eks-cluster my-cluster --instance-types t3.medium,t3.large

# Custom scaling configuration
k8s-helper create-eks-cluster my-cluster --min-size 2 --max-size 10 --desired-size 5
```

#### New create-nodegroup command
```bash
# Create a node group manually
k8s-helper create-nodegroup my-cluster my-nodegroup

# Create with specific configuration
k8s-helper create-nodegroup my-cluster my-nodegroup \
  --instance-types t3.large,t3.xlarge \
  --capacity-type SPOT \
  --min-size 3 --max-size 20 --desired-size 10
```

#### New list-nodegroups command
```bash
# List node groups for a cluster
k8s-helper list-nodegroups my-cluster

# JSON output
k8s-helper list-nodegroups my-cluster --output json

# YAML output
k8s-helper list-nodegroups my-cluster --output yaml
```

### Key Features

1. **Automatic IAM Role Creation**: Creates required IAM roles for both cluster and node groups
2. **Subnet Management**: Automatically selects or creates subnets across availability zones
3. **Instance Type Flexibility**: Support for multiple instance types and capacity types
4. **Scaling Configuration**: Configurable min/max/desired node counts
5. **Wait for Ready**: Optional waiting for cluster and node group to be active

### Usage Examples

#### Complete EKS Setup
```bash
# Create cluster with node group and wait for completion
k8s-helper create-eks-cluster production-cluster \
  --region us-west-2 \
  --version 1.29 \
  --instance-types t3.medium,t3.large \
  --min-size 2 \
  --max-size 20 \
  --desired-size 6 \
  --wait

# Configure kubectl
aws eks update-kubeconfig --name production-cluster --region us-west-2

# Verify nodes
kubectl get nodes
```

#### Manual Node Group Creation
```bash
# Create cluster without node group
k8s-helper create-eks-cluster my-cluster --no-nodegroup

# Create node group later
k8s-helper create-nodegroup my-cluster worker-nodes \
  --instance-types t3.medium \
  --capacity-type ON_DEMAND \
  --min-size 1 \
  --max-size 5 \
  --desired-size 3

# List node groups
k8s-helper list-nodegroups my-cluster
```

### Benefits

- **No Empty Clusters**: Default behavior creates working clusters with nodes
- **Production Ready**: Proper IAM roles, subnets, and security groups
- **Cost Optimization**: Support for SPOT instances and flexible scaling
- **Easy Management**: Simple CLI commands for common operations

### Migration from v0.2.3

Existing commands continue to work. The only change is that node groups are now created by default. To maintain the old behavior (cluster only), use `--no-nodegroup`.

### Error Handling

The CLI provides helpful error messages and troubleshooting tips:
- AWS credentials setup
- VPC and subnet configuration
- IAM permissions
- Cluster and node group status

This update resolves the issue where `kubectl get nodes` returned "No resources found" by ensuring clusters have worker nodes by default.
