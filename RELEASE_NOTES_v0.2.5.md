# k8s-helper-cli v0.2.5 Release Notes

## 🔧 Bug Fixes

### EKS Node Group Creation Fix
- **Fixed**: Node group creation failing with `Parameter validation failed: Invalid type for parameter remoteAccess.ec2SshKey, value: None`
- **Root Cause**: The `create_nodegroup` method was always passing `remoteAccess={'ec2SshKey': None}` to the AWS API, but AWS expects either a valid SSH key string or no `remoteAccess` parameter at all.
- **Solution**: Modified the method to conditionally include the `remoteAccess` parameter only when an SSH key is provided.

## ✨ New Features

### SSH Key Support
- **Added**: `--ssh-key` parameter to `create-nodegroup` command
- **Usage**: `k8s-helper create-nodegroup cluster-name nodegroup-name --ssh-key my-key-pair`
- **Optional**: SSH key is optional - when not provided, no `remoteAccess` is sent to AWS

## 🚀 Installation

```bash
pip install k8s-helper-cli==0.2.5
```

## 📖 Usage Examples

### Create Node Group (No SSH Key)
```bash
k8s-helper create-nodegroup todo-cluster todo-nodes \
  --region ap-south-1 \
  --instance-types t3.micro \
  --min-size 1 \
  --max-size 1 \
  --desired-size 1
```

### Create Node Group (With SSH Key)
```bash
k8s-helper create-nodegroup todo-cluster todo-nodes \
  --region ap-south-1 \
  --instance-types t3.micro \
  --min-size 1 \
  --max-size 1 \
  --desired-size 1 \
  --ssh-key my-key-pair
```

### Create EKS Cluster with Auto Node Group
```bash
k8s-helper create-eks-cluster todo-cluster \
  --region ap-south-1 \
  --version 1.29 \
  --node-group todo-nodes \
  --instance-types t3.micro \
  --min-size 1 \
  --max-size 1 \
  --desired-size 1 \
  --create-nodegroup \
  --wait
```

## 🔍 What's Fixed

1. **Node Group Creation**: Now works correctly without SSH keys
2. **AWS API Compliance**: Proper parameter handling for AWS EKS APIs
3. **Error Handling**: Better error messages and validation
4. **CLI Enhancement**: New SSH key parameter support

## 📋 Migration Notes

- **Backward Compatible**: All existing commands continue to work
- **No Breaking Changes**: Default behavior unchanged
- **New Optional Parameter**: `--ssh-key` is optional for `create-nodegroup`

## 🎯 Next Steps After Installing

1. **Test Node Group Creation**:
   ```bash
   k8s-helper create-nodegroup your-cluster your-nodegroup --region your-region
   ```

2. **Verify Nodes**:
   ```bash
   kubectl get nodes
   ```

3. **Deploy Applications**:
   ```bash
   k8s-helper apply my-app nginx:latest
   ```

## 🔗 Links

- **PyPI**: https://pypi.org/project/k8s-helper-cli/0.2.5/
- **GitHub**: https://github.com/your-repo/k8s-helper
- **Documentation**: See README.md for full documentation

---

**Version**: 0.2.5  
**Release Date**: July 16, 2025  
**Previous Version**: 0.2.4
