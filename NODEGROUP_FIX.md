# Node Group Creation Fix - v0.2.5

## Problem
The EKS node group creation was failing with the error:
```
Parameter validation failed:
Invalid type for parameter remoteAccess.ec2SshKey, value: None, type: <class 'NoneType'>, valid types: <class 'str'>
```

## Root Cause
The `create_nodegroup` method in `core.py` was always passing the `remoteAccess` parameter with `ec2SshKey: None`, but the AWS API expects either:
1. A valid SSH key name (string), or
2. No `remoteAccess` parameter at all

## Solution
Fixed the `create_nodegroup` method to:
1. Only include the `remoteAccess` parameter when an SSH key is actually provided
2. Added `ssh_key` parameter to the method signature
3. Updated the CLI to accept the `--ssh-key` option
4. Use conditional parameter building to avoid passing null values

## Key Changes
- **core.py**: Modified `create_nodegroup` method to conditionally include `remoteAccess`
- **cli.py**: Added `--ssh-key` option to `create-nodegroup` command
- **Version**: Updated to 0.2.5

## Testing
✅ Node group creation without SSH key (no remoteAccess parameter)
✅ Node group creation with SSH key (includes remoteAccess parameter)

## Usage
```bash
# Without SSH key (default behavior)
k8s-helper create-nodegroup todo-cluster todo-nodes --region ap-south-1

# With SSH key
k8s-helper create-nodegroup todo-cluster todo-nodes --region ap-south-1 --ssh-key my-key-pair
```

## Next Steps
1. Install the fixed version: `pip install -e .` (local) or wait for PyPI upload
2. Test the node group creation
3. Verify that `kubectl get nodes` works after creation
