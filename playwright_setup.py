import subprocess
import sys

def ensure_playwright():
    try:
        # Try to import Playwright — if it works, skip
        from playwright.sync_api import sync_playwright
    except:
        pass

    # Install Chromium (needed for Playwright browser)
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except:
        pass
