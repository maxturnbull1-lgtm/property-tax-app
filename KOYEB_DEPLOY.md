# Deploy to Koyeb

This guide will help you deploy the Michigan Property Tax Estimator to Koyeb.

## Prerequisites

- Your code must be in a GitHub repository (✅ Already done!)
- GitHub repository: `maxturnbull1-lgtm/property-tax-app`

## Deployment Steps

### Step 1: Sign Up for Koyeb

1. Go to **https://www.koyeb.com/**
2. Click "Get Started" or "Sign Up"
3. Sign up with your GitHub account (recommended for easy deployment)

### Step 2: Create a New Service

1. Once logged in, click **"Create Service"** in the dashboard
2. Select **"GitHub"** as your source
3. Authorize Koyeb to access your GitHub repositories if prompted

### Step 3: Configure Your Service

1. **Select Repository**: Choose `maxturnbull1-lgtm/property-tax-app`
2. **Branch**: Select `main`
3. **Build**: 
   - **Build Command**: `pip install -r requirements.txt`
   - Koyeb will auto-detect Python
4. **Run**:
   - **Run Command**: Leave empty (uses Procfile) OR specify:
     ```
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
     ```

### Step 4: Configure Environment

Koyeb automatically:
- Sets the `PORT` environment variable
- Detects Python from `requirements.txt`
- Uses the `Procfile` for startup

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for the build to complete (2-5 minutes)
3. Your app will be live at: `https://your-app-name.koyeb.app`

## Configuration Details

### Files Used:
- **`Procfile`**: Tells Koyeb how to run your app
- **`requirements.txt`**: Python dependencies
- **`cloud_scraper.py`**: Cloud-compatible scraper (used automatically)
- **`.streamlit/config.toml`**: Streamlit configuration

### Automatic Detection:
- The app automatically detects Koyeb environment via `PORT` environment variable
- Uses Chrome/Chromium (pre-installed on Koyeb) instead of Edge
- Uses optimized cloud scraper

## Post-Deployment

### View Logs
- Go to your service dashboard
- Click "Logs" to see real-time application logs

### Update Your App
1. Make changes and push to GitHub:
   ```powershell
   git add .
   git commit -m "Your changes"
   git push
   ```
2. Koyeb will automatically redeploy (if auto-deploy is enabled)

### Custom Domain (Optional)
1. Go to your service settings
2. Click "Domains"
3. Add your custom domain

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Verify Python version (Koyeb uses Python 3.9+ by default)
- Check build logs in Koyeb dashboard

### App Won't Start
- Verify the Procfile is correct
- Check that `app.py` is in the root directory
- Review logs in Koyeb dashboard

### Selenium/Chrome Issues
- The app uses `cloud_scraper.py` automatically on Koyeb
- Chrome/Chromium is pre-installed on Koyeb
- If issues persist, check logs for Chrome driver errors

### Database File Missing
- Ensure `all_millage_rates.db` is committed to Git
- Check file size (Koyeb has limits on file sizes)

## Koyeb Features

- **Free Tier**: Includes generous free tier for testing
- **Auto-Scaling**: Automatically scales based on traffic
- **SSL/HTTPS**: Automatic SSL certificates
- **GitHub Integration**: Automatic deployments on push
- **Global CDN**: Fast access worldwide

## Support

- Koyeb Docs: https://www.koyeb.com/docs
- Koyeb Support: Available in the dashboard

---

## Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] Koyeb account created
- [ ] Service created and connected to GitHub
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Procfile exists and is correct
- [ ] Deployed successfully
- [ ] App accessible via URL

Your app should now be live on Koyeb! 🚀
