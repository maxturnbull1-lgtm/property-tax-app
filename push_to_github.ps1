# PowerShell script to push to GitHub
# Usage: .\push_to_github.ps1 <github-repo-url>
# Example: .\push_to_github.ps1 https://github.com/username/property-tax-app.git

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl
)

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "Pushing to GitHub..." -ForegroundColor Green

# Check if Git is installed
try {
    git --version | Out-Null
} catch {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists: $remoteExists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to update it? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        git remote set-url origin $RepoUrl
        Write-Host "Remote URL updated" -ForegroundColor Green
    }
} else {
    git remote add origin $RepoUrl
    Write-Host "Remote 'origin' added" -ForegroundColor Green
}

# Ensure we're on main branch
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    git checkout -b main
    $currentBranch = "main"
}

if ($currentBranch -ne "main") {
    Write-Host "Renaming branch to 'main'..." -ForegroundColor Cyan
    git branch -M main
}

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
try {
    git push -u origin main
    Write-Host "`nSuccessfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: $RepoUrl" -ForegroundColor Cyan
} catch {
    Write-Host "`nERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Make sure you have:" -ForegroundColor Yellow
    Write-Host "1. Created the repository on GitHub" -ForegroundColor White
    Write-Host "2. Authenticated with GitHub (use GitHub CLI or SSH keys)" -ForegroundColor White
    Write-Host "3. Have push permissions to the repository" -ForegroundColor White
    exit 1
}
