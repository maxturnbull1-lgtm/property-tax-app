# GitHub Setup Instructions

This guide will help you set up Git and push this project to GitHub.

## Step 1: Install Git

If Git is not installed on your computer:

1. Download Git for Windows from: https://git-scm.com/download/win
2. Run the installer and follow the setup wizard
3. Restart PowerShell/Command Prompt after installation

## Step 2: Verify Git Installation

Open PowerShell and run:
```powershell
git --version
```

You should see something like: `git version 2.x.x`

## Step 3: Configure Git (First Time Only)

Set your name and email (replace with your GitHub credentials):
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 4: Set Up the Repository

### Option A: Using the Setup Script (Recommended)

1. Navigate to the project directory:
```powershell
cd C:\Users\Max_t\Downloads\PropertyTaxApp\PropertyTaxApp
```

2. Run the setup script:
```powershell
.\setup_git.ps1
```

This will:
- Initialize the Git repository
- Add all files
- Create an initial commit
- Show you the next steps

### Option B: Manual Setup

1. Navigate to the project directory:
```powershell
cd C:\Users\Max_t\Downloads\PropertyTaxApp\PropertyTaxApp
```

2. Initialize Git:
```powershell
git init
```

3. Add all files:
```powershell
git add .
```

4. Create initial commit:
```powershell
git commit -m "Initial commit: Michigan Property Tax Estimator app"
```

5. Create and switch to main branch:
```powershell
git checkout -b main
```

## Step 5: Create GitHub Repository

1. Go to https://github.com/new
2. Sign in to your GitHub account (create one if needed)
3. Fill in the repository details:
   - **Repository name**: `property-tax-app` (or your preferred name)
   - **Description**: "Michigan Property Tax Estimator - Streamlit app"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

## Step 6: Push to GitHub

### Option A: Using the Push Script

After creating the repository on GitHub, copy the repository URL (e.g., `https://github.com/username/property-tax-app.git`) and run:

```powershell
.\push_to_github.ps1 https://github.com/username/property-tax-app.git
```

Replace `username` and `property-tax-app` with your actual GitHub username and repository name.

### Option B: Manual Push

1. Add the remote repository:
```powershell
git remote add origin https://github.com/username/property-tax-app.git
```
(Replace with your actual repository URL)

2. Rename branch to main (if needed):
```powershell
git branch -M main
```

3. Push to GitHub:
```powershell
git push -u origin main
```

## Authentication

When pushing, you may be prompted for credentials:

- **Personal Access Token**: GitHub no longer accepts passwords. You'll need to create a Personal Access Token:
  1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Click "Generate new token (classic)"
  3. Give it a name and select scopes: `repo` (full control of private repositories)
  4. Copy the token and use it as your password when prompted

- **GitHub CLI**: Alternatively, install GitHub CLI and authenticate:
  ```powershell
  winget install --id GitHub.cli
  gh auth login
  ```

## Troubleshooting

### "Git is not recognized"
- Make sure Git is installed and added to PATH
- Restart PowerShell after installation

### "Permission denied" or "Authentication failed"
- Use a Personal Access Token instead of password
- Make sure you have push permissions to the repository

### "Repository not found"
- Check that the repository URL is correct
- Make sure the repository exists on GitHub
- Verify you have access to the repository

## Next Steps

After successfully pushing to GitHub:

1. Your code is now on GitHub! 🎉
2. You can view it at: `https://github.com/username/property-tax-app`
3. You can clone it on other machines with: `git clone https://github.com/username/property-tax-app.git`
4. To make future changes:
   ```powershell
   git add .
   git commit -m "Description of changes"
   git push
   ```

## Files Included in Repository

The `.gitignore` file is configured to exclude:
- Virtual environment (`venv/`)
- Python cache files (`__pycache__/`)
- IDE files
- OS-specific files
- Log files

The following important files ARE included:
- All Python source files (`.py`)
- `requirements.txt`
- `README.md`
- Database file (`all_millage_rates.db`)
- WebDriver (`msedgedriver.exe`)
- Excel files (if needed)

Note: Large binary files like `msedgedriver.exe` and database files are included. If your repository becomes too large, consider using Git LFS (Large File Storage) or hosting these files elsewhere.
