# cloud_scraper.py
# Cloud-compatible scraper using Selenium with Chrome (works on Linux cloud platforms)

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

HTL_HOME = "https://michigan.hometownlocator.com/"
LOOKUP_URL = "https://michigan.hometownlocator.com/maps/address-lookup.cfm"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _parse_address_page(html: str) -> Dict[str, Optional[str]]:
    """
    Parse HometownLocator page HTML into {township, county, school_district}.
    """
    soup = BeautifulSoup(html, "html.parser")
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
    """
    try:
        r = requests.get(
            LOOKUP_URL,
            params={"addr": address},
            headers=HEADERS,
            timeout=20,
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
    
    # User agent
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    # Unique profile dir
    tmp_ud = tempfile.mkdtemp(prefix="chromedata_")
    opts.add_argument(f"--user-data-dir={tmp_ud}")

    # For cloud platforms, Chrome/Chromium is typically installed system-wide
    # Selenium will use chromedriver from PATH or we can use webdriver_manager
    try:
        # Try using webdriver_manager if available (handles driver installation)
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
    except ImportError:
        # Fallback: use system chromedriver
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=opts)
    
    driver.set_page_load_timeout(40)
    
    return driver, tmp_ud


def get_township_school_from_address(address: str, headless: bool = True) -> dict:
    """
    Return {township, county, school_district} for an address.
    Fast path first; fallback to Selenium if needed.
    Cloud-compatible version using Chrome.
    """

    # ---- FAST PATH (no browser) ----
    fast = _try_fast_lookup(address)
    if fast:
        return fast

    # ---- SELENIUM FALLBACK (Chrome for cloud) ----
    driver = None
    tmp_ud = None

    try:
        driver, tmp_ud = _create_chrome_driver(headless=headless)
        wait = WebDriverWait(driver, 25)

        driver.get(HTL_HOME)

        search = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".address_input.localsearchmapfield"))
        )
        search.clear()
        search.send_keys(address)
        search.send_keys(Keys.RETURN)

        # If results list appears, click first result
        try:
            first = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.list-group a")))
            first.click()
        except Exception:
            pass

        # wait for page content to appear
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.halfcontentpadded")))

        parsed = _parse_address_page(driver.page_source)
        return parsed

    except Exception as e:
        return {"error": str(e)}

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
