# k8s-helper-cli v0.2.7 - Bug Fix Release

## 🐛 Bug Fixes

### Fixed "Only one live display may be active at once" Error

**Issue:** The CLI was throwing a "Only one live display may be active at once" error when running EKS cluster creation commands with the `--wait` flag.

**Root Cause:** Overlapping `rich.console.status()` displays in the CLI code were causing conflicts when multiple status displays were active simultaneously.

**Fix:** Removed nested `with console.status()` blocks in:
- `create_nodegroup` command 
- `create_eks_cluster` command

**Commands Fixed:**
- `k8s-helper create-eks-cluster --wait`
- `k8s-helper create-nodegroup --wait`

**Testing:** 
- ✅ Unit tests confirm no overlapping displays
- ✅ CLI commands work correctly with and without `--wait` flag
- ✅ SSH key option (`--ssh-key`) continues to work properly
- ✅ Package builds and installs successfully
- ✅ Published to PyPI and verified installation

## 🔧 Technical Details

The fix ensures that long-running operations (like waiting for cluster/node group creation) display progress messages directly rather than through nested status displays, preventing the Rich library conflict.

## 📦 Installation

```bash
pip install k8s-helper-cli==0.2.7
```

## ✅ Verification

After upgrading, you can now run:

```bash
k8s-helper create-eks-cluster my-cluster --wait
k8s-helper create-nodegroup my-cluster my-nodegroup --wait
```

Without encountering the "Only one live display may be active at once" error.

## 🔄 Backwards Compatibility

This is a bug fix release with no breaking changes. All existing functionality remains the same.
