# GitHub Setup Guide

This project is now ready to be uploaded to GitHub!

## Files Created for GitHub

1. **`.gitignore`** - Excludes virtual environment, cache files, and other unnecessary files
2. **`README.md`** - Main project documentation
3. **`SETUP.md`** - Detailed setup instructions
4. **`requirements.txt`** - Python dependencies

## Next Steps to Upload to GitHub

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it (e.g., `lab1_data_engineering`)
4. Choose public or private
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 2. Add Remote and Push

Run these commands in your project directory:

```bash
# Make sure you're in the project directory
cd /home/horhoro/projects/lab1_data_engineering

# Add all files (respecting .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: Data engineering pipeline with extraction, transformation, and dashboard"

# Add your GitHub repository as remote (replace with your actual URL)
git remote add origin https://github.com/YOUR_USERNAME/lab1_data_engineering.git

# Rename branch to main (GitHub standard)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 3. Verify Upload

Check your GitHub repository page - you should see all your files!

## What Gets Uploaded

✅ **Included:**
- All source code (`src/`)
- Data directory structure (but large files may be excluded if you uncomment them in .gitignore)
- Configuration files (`.gitignore`, `requirements.txt`)
- Documentation (`README.md`, `SETUP.md`)
- Dashboard output (unless you uncomment the exclusion in .gitignore)

❌ **Excluded (via .gitignore):**
- Virtual environment (`venv/`)
- Python cache files (`__pycache__/`)
- IDE files (`.vscode/`, `.idea/`)
- Temporary files

## Optional: Exclude Large Data Files

If your data files are very large, you may want to exclude them from git. Edit `.gitignore` and uncomment these lines:

```
# data/processed/*.jsonl
# data/processed/*.json
# data/processed/*.csv
```

Then add a `data/processed/.gitkeep` file to preserve the directory structure:

```bash
touch data/processed/.gitkeep
git add data/processed/.gitkeep
```

## Repository Settings

After uploading, consider:
1. Adding a description on GitHub
2. Adding topics/tags (e.g., `data-engineering`, `python`, `analytics`)
3. Adding a license file
4. Enabling GitHub Pages if you want to host the dashboard

## Troubleshooting

### Authentication Issues
If `git push` asks for credentials:
- Use a Personal Access Token instead of password
- Or set up SSH keys for GitHub

### Large Files
If files are too large for GitHub (>100MB):
- Use Git LFS (Large File Storage)
- Or exclude large data files from git

### Branch Name
If you prefer `master` instead of `main`:
```bash
git branch -M master
git push -u origin master
```

