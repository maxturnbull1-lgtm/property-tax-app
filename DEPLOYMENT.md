# Deployment Guide

This guide will help you deploy the Michigan Property Tax Estimator to the web.

## Option 1: Streamlit Community Cloud (Recommended - Free & Easy)

Streamlit Community Cloud is the easiest way to deploy Streamlit apps for free.

### Prerequisites
- Your code must be in a GitHub repository (✅ Already done!)
- Repository must be public (or you need a paid Streamlit account)

### Steps

1. **Sign up for Streamlit Community Cloud**
   - Go to https://share.streamlit.io/
   - Click "Sign up" and sign in with your GitHub account
   - Authorize Streamlit to access your GitHub repositories

2. **Deploy Your App**
   - Click "New app" in the Streamlit Community Cloud dashboard
   - Select your repository: `maxturnbull1-lgtm/property-tax-app`
   - Select branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Wait for Deployment**
   - Streamlit will automatically:
     - Install dependencies from `requirements.txt`
     - Build your app
     - Deploy it to a public URL
   - This usually takes 2-5 minutes

4. **Access Your App**
   - Once deployed, you'll get a URL like: `https://property-tax-app-xxxxx.streamlit.app`
   - Share this URL with anyone!

### Important Notes for Cloud Deployment

- **Selenium/Chrome**: The app uses a cloud-compatible scraper that works with Chrome/Chromium in headless mode
- **Database**: The `all_millage_rates.db` file is included in the repository and will be available
- **WebDriver**: Uses `webdriver-manager` to automatically download the correct ChromeDriver

### Troubleshooting

If deployment fails:
1. Check the deployment logs in Streamlit Community Cloud
2. Ensure all dependencies are in `requirements.txt`
3. Verify the database file is included in the repository
4. Check that `app.py` is in the root directory

---

## Option 2: Other Cloud Platforms

### Render

1. Go to https://render.com
2. Sign up and connect your GitHub account
3. Create a new "Web Service"
4. Connect your repository
5. Build command: `pip install -r requirements.txt`
6. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Railway

1. Go to https://railway.app
2. Sign up and connect GitHub
3. Create a new project from GitHub
4. Select your repository
5. Railway will auto-detect and deploy

### Fly.io

1. Install Fly CLI: `winget install flyctl`
2. Run: `fly launch`
3. Follow the prompts to deploy

---

## Option 3: Self-Hosted (VPS/Server)

If you have your own server:

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip chromium-browser chromium-chromedriver
   pip3 install -r requirements.txt
   ```

2. **Run the App**
   ```bash
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

3. **Use a Reverse Proxy** (Nginx recommended)
   - Configure Nginx to proxy requests to `localhost:8501`
   - Set up SSL with Let's Encrypt

---

## Environment Variables (Optional)

You can set these in your cloud platform's environment settings:

- `STREAMLIT_SERVER_PORT`: Automatically set by most platforms
- `STREAMLIT_SHARING`: Set to "true" for Streamlit Community Cloud

---

## Post-Deployment

After deployment:
1. Test the app with a sample address
2. Monitor the logs for any errors
3. Share your app URL!

Your app will be live and accessible to anyone with the URL! 🎉
