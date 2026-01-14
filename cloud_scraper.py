# cloud_scraper.py
# Cloud-compatible scraper using Selenium with Chrome (works on Linux cloud platforms like Koyeb)

import os
import re
import tempfile
import shutil
from typing import Optional, Dict, Tuple

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Try to use lxml parser (faster), fall back to html.parser
try:
    import lxml
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"

HTL_HOME = "https://michigan.hometownlocator.com/"
LOOKUP_URL = "https://michigan.hometownlocator.com/maps/address-lookup.cfm"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Cache for address lookups (in-memory, persists for session)
_address_cache: Dict[str, dict] = {}


def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _parse_address_page(html: str) -> Dict[str, Optional[str]]:
    """
    Parse HometownLocator page HTML into {township, county, school_district}.
    """
    soup = BeautifulSoup(html, PARSER)
    result: Dict[str, Optional[str]] = {"township": None, "county": None, "school_district": None}

    for section in soup.find_all("div", class_="halfcontentpadded"):
        h2 = section.find("h2")
        heading = _clean_text(h2.get_text()).lower() if h2 else ""

        # Township / County
        if any(k in heading for k in ["administrative", "geographic units", "census"]):
            for li in section.find_all("li"):
                txt = _clean_text(li.get_text(" "))
                low = txt.lower()

                if any(k in low for k in ["city of", "township", "village of", "charter township"]):
                    result["township"] = txt

                if "county" in low:
                    result["county"] = txt.split(":")[-1].strip() if ":" in txt else txt

        # School District
        if any(k in heading for k in ["school district", "school zones", "schools", "school"]):
            a = section.find("a")
            if a and not result["school_district"]:
                candidate = _clean_text(a.get_text())
                if len(candidate) >= 4:
                    result["school_district"] = candidate

            for li in section.find_all("li"):
                txt = _clean_text(li.get_text(" "))
                if re.search(r"(public\s+schools?|school\s+district)", txt, re.I):
                    result["school_district"] = txt

    # Fallback global scan for school district
    if not result["school_district"]:
        for a in soup.find_all("a"):
            t = _clean_text(a.get_text())
            if re.search(r"(public\s+schools?|school\s+district)", t, re.I):
                result["school_district"] = t
                break

    # Light normalization
    for k in list(result.keys()):
        if isinstance(result[k], str):
            result[k] = result[k].replace("County:", "").strip()

    return result


def _try_fast_lookup(address: str) -> Optional[dict]:
    """
    Try HTTP fetch (no browser). Return parsed dict or None to indicate fallback.
    Optimized with shorter timeout and connection reuse.
    """
    try:
        session = requests.Session()
        r = session.get(
            LOOKUP_URL,
            params={"addr": address},
            headers=HEADERS,
            timeout=10,
            allow_redirects=True,
        )
        if r.status_code != 200:
            return None

        html = r.text
        if "halfcontentpadded" not in html.lower():
            return None

        parsed = _parse_address_page(html)
        if parsed.get("township") or parsed.get("school_district"):
            return parsed
        return None
    except Exception:
        return None


def _create_chrome_driver(headless: bool = True) -> Tuple[webdriver.Chrome, str]:
    """
    Create Chrome driver for cloud deployment (works on Linux).
    Returns (driver, temp_user_data_dir).
    """
    opts = ChromeOptions()
    
    if headless:
        opts.add_argument("--headless=new")
    
    # Cloud deployment options
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--log-level=3")
    opts.add_argument("--window-size=1200,900")
    opts.add_argument("--single-process")  # Important for some cloud platforms
    
    # User agent
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    # Speed optimizations - disable images
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
    }
    opts.add_experimental_option("prefs", prefs)
    opts.add_argument("--blink-settings=imagesEnabled=false")
    
    # Unique profile dir
    tmp_ud = tempfile.mkdtemp(prefix="chromedata_")
    opts.add_argument(f"--user-data-dir={tmp_ud}")

    # For cloud platforms, specify Chrome binary location explicitly
    # Try multiple common locations for Chrome/Chromium
    chrome_binary_locations = [
        "/usr/bin/chromium-browser",  # Most common on Ubuntu/Debian
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/snap/bin/chromium",
        "/usr/lib/chromium-browser/chromium-browser",
    ]
    
    chrome_binary = None
    for location in chrome_binary_locations:
        if os.path.exists(location):
            chrome_binary = location
            break
    
    # Also try using 'which' command as fallback
    if not chrome_binary:
        import subprocess
        for cmd in ["chromium-browser", "chromium", "google-chrome", "google-chrome-stable"]:
            try:
                result = subprocess.run(["which", cmd], capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    chrome_binary = result.stdout.strip()
                    break
            except Exception:
                pass
    
    if chrome_binary:
        opts.binary_location = chrome_binary
    
    # Use webdriver_manager for driver, which handles Chrome binary detection
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        
        # Try to use webdriver_manager
        if chrome_binary and "chromium" in chrome_binary.lower():
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        else:
            service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=opts)
    except Exception as e:
        # Fallback: try system chromedriver
        try:
            chromedriver_paths = [
                "/usr/bin/chromedriver",
                "/usr/local/bin/chromedriver",
                "/snap/bin/chromium.chromedriver",
            ]
            chromedriver_path = None
            for path in chromedriver_paths:
                if os.path.exists(path):
                    chromedriver_path = path
                    break
            
            if chromedriver_path:
                service = ChromeService(executable_path=chromedriver_path)
            else:
                service = ChromeService()
            
            driver = webdriver.Chrome(service=service, options=opts)
        except Exception as e2:
            raise Exception(
                f"Could not initialize Chrome driver. "
                f"Chrome binary searched: {chrome_binary_locations}, "
                f"Found: {chrome_binary}, "
                f"Error: {str(e2)}"
            )
    
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(10)
    
    return driver, tmp_ud


def get_township_school_from_address(address: str, headless: bool = True) -> dict:
    """
    Return {township, county, school_district} for an address.
    Fast path first; fallback to Selenium if needed.
    Cloud-compatible version using Chrome.
    """
    # Normalize address for cache key
    cache_key = address.strip().lower()
    
    # Check cache first
    if cache_key in _address_cache:
        return _address_cache[cache_key]

    # ---- FAST PATH (no browser) ----
    fast = _try_fast_lookup(address)
    if fast:
        _address_cache[cache_key] = fast
        return fast

    # ---- SELENIUM FALLBACK (Chrome for cloud) ----
    driver = None
    tmp_ud = None

    try:
        driver, tmp_ud = _create_chrome_driver(headless=headless)
        wait = WebDriverWait(driver, 15)

        driver.get(HTL_HOME)

        search = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".address_input.localsearchmapfield"))
        )
        search.clear()
        search.send_keys(address)
        search.send_keys(Keys.RETURN)

        # If results list appears, click first result
        try:
            first = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.list-group a"))
            )
            first.click()
        except Exception:
            pass

        # Wait for page content
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.halfcontentpadded"))
        )

        parsed = _parse_address_page(driver.page_source)
        
        # Cache successful results
        if "error" not in parsed:
            _address_cache[cache_key] = parsed
        
        return parsed

    except Exception as e:
        error_result = {"error": str(e)}
        return error_result

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        if tmp_ud:
            try:
                shutil.rmtree(tmp_ud, ignore_errors=True)
            except Exception:
                pass
