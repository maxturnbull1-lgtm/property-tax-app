# Quick Start: Push to GitHub

Your Git repository is ready! Follow these steps to publish it to GitHub:

## Step 1: Configure Your Git Identity (Optional but Recommended)

If you want to use your own name and email for commits:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Sign in (or create an account if needed)
3. Repository name: `property-tax-app` (or your choice)
4. Description: "Michigan Property Tax Estimator - Streamlit app"
5. Choose Public or Private
6. **DO NOT** check "Initialize with README" (we already have files)
7. Click "Create repository"

## Step 3: Push to GitHub

After creating the repository, GitHub will show you commands. Use this one:

```powershell
cd C:\Users\Max_t\Downloads\PropertyTaxApp\PropertyTaxApp
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

**OR** use the automated script:

```powershell
.\push_to_github.ps1 https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

## Authentication

When pushing, you'll be prompted for credentials. Use:
- **Username**: Your GitHub username
- **Password**: A Personal Access Token (not your GitHub password)

To create a token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select `repo` scope
4. Copy the token and use it as your password

## Done! 🎉

Your code is now on GitHub. View it at: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
