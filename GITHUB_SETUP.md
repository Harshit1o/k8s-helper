# How to Push k8s-helper to GitHub

## 🚀 Step-by-Step Guide

### 1. Initialize Git Repository (if not already done)
```bash
cd "c:\Users\hp\OneDrive\Documents\Open-source\k8s-helper"
git init
```

### 2. Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository" (+ icon in top right)
3. Repository name: `k8s-helper`
4. Description: `A simplified Python wrapper for common Kubernetes operations`
5. Choose Public or Private
6. **Don't** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 3. Add Files to Git
```bash
# Add all files
git add .

# Check what's being added
git status

# Make initial commit
git commit -m "Initial commit: k8s-helper Python library

- Complete Kubernetes wrapper with pod, deployment, service management
- Rich CLI interface with typer and rich
- Comprehensive error handling and validation
- Unit tests and integration tests
- CI/CD pipeline with GitHub Actions
- Documentation and examples"
```

### 4. Connect to GitHub Repository
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/k8s-helper.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/k8s-helper.git
```

### 5. Push to GitHub
```bash
# Push to main branch
git branch -M main
git push -u origin main
```

### 6. Verify Upload
1. Go to your GitHub repository
2. Check that all files are there
3. Verify the README.md displays correctly

## 📋 Pre-Push Checklist

Before pushing, make sure you have:

- ✅ **All files committed**: Check with `git status`
- ✅ **Tests passing**: Run `python test_installation.py`
- ✅ **No sensitive data**: Review files for passwords, tokens, etc.
- ✅ **LICENSE file**: MIT license included
- ✅ **README.md**: Complete documentation
- ✅ **CHANGELOG.md**: Version history
- ✅ **.gitignore**: Excludes unnecessary files

## 🔧 Post-Push Setup

### 1. Enable GitHub Actions
- GitHub Actions should automatically run on push
- Check the "Actions" tab in your repository
- Fix any failing tests

### 2. Set up Branch Protection (Optional)
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select your CI/CD checks

### 3. Add Repository Secrets (For Publishing)
If you plan to publish to PyPI:
1. Go to Settings → Secrets and variables → Actions
2. Add `PYPI_API_TOKEN` with your PyPI token

### 4. Configure Codecov (Optional)
1. Go to [Codecov.io](https://codecov.io)
2. Sign up with GitHub
3. Add your repository
4. Get the upload token and add as `CODECOV_TOKEN` secret

## 📦 Publishing to PyPI

### 0. Set Up PyPI Account and API Token
**Before you can publish, you need:**

1. **Create accounts:**
   - [PyPI Account](https://pypi.org/account/register/) (for production)
   - [TestPyPI Account](https://test.pypi.org/account/register/) (for testing)

2. **Get API tokens:**
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/) → API tokens
   - Create a new token with "Entire account" scope
   - Copy the token (starts with `pypi-`)
   - Do the same for [TestPyPI](https://test.pypi.org/manage/account/)

3. **Configure authentication:**
   ```bash
   # Create .pypirc file in your home directory
   # Windows: C:\Users\hp\.pypirc
   # Add this content:
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-YOUR_PYPI_TOKEN_HERE

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-YOUR_TESTPYPI_TOKEN_HERE
   ```

### 1. Build the Package
```bash
# Make sure you're in the k8s-helper directory
cd "C:\Users\hp\OneDrive\Documents\Open-source\k8s-helper"

# Build the package (you've already done this!)
python -m build
```

**Important for Windows with virtual environment:**
Use the full Python path: `C:/Users/hp/OneDrive/Documents/Open-source/.venv/Scripts/python.exe -m build`

This creates two files in the `dist/` directory:
- `k8s_helper-0.1.0.tar.gz` (source distribution)
- `k8s_helper-0.1.0-py3-none-any.whl` (wheel distribution)

### 2. Check Package Before Upload
```bash
# Check if the package is valid
python -m twine check dist/*
```

**Windows with virtual environment:**
```bash
C:/Users/hp/OneDrive/Documents/Open-source/.venv/Scripts/python.exe -m twine check dist/*
```

### 3. Test Upload to TestPyPI (Optional but Recommended)
```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ k8s-helper
```

**Windows with virtual environment:**
```bash
C:/Users/hp/OneDrive/Documents/Open-source/.venv/Scripts/python.exe -m twine upload --repository testpypi dist/*
```

### 4. Upload to PyPI
```bash
# Upload to the real PyPI
python -m twine upload dist/*
```

**Windows with virtual environment:**
```bash
C:/Users/hp/OneDrive/Documents/Open-source/.venv/Scripts/python.exe -m twine upload dist/*
```

### 5. Verify Publication
```bash
# Install from PyPI
pip install k8s-helper

# Test it works
k8s-helper --help
```

## 🎯 Next Steps After Push

1. **Test CI/CD**: Make a small change and push to test the pipeline
2. **Write Documentation**: Add more examples and use cases
3. **Create Issues**: Plan future features and improvements
4. **Community**: Share your project, get feedback
5. **Publish**: Consider publishing to PyPI for easy installation

## 🔍 Troubleshooting

### Common Issues
- **Large files**: Use Git LFS if you have large files
- **Permission denied**: Check SSH keys or use HTTPS
- **Authentication failed**: Verify username/password or token
- **Files not showing**: Check .gitignore isn't excluding too much

### Getting Help
- GitHub Documentation: https://docs.github.com
- Git Documentation: https://git-scm.com/doc
- k8s-helper Issues: Create an issue in your repository

---

**🎉 Ready to push? Follow the steps above and your k8s-helper library will be live on GitHub!**
