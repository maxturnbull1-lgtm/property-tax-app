# selenium_scraper.py

import os
import re
import tempfile
import shutil
from typing import Optional, Dict, Tuple

import requests
from bs4 import BeautifulSoup

# Try to use lxml parser (faster), fall back to html.parser
try:
    import lxml
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
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
    Uses lxml parser if available (faster), falls back to html.parser.
    """
    # Use faster parser if available
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
                    # Normalize "County: Kent County" -> "Kent County" if needed
                    result["county"] = txt.split(":")[-1].strip() if ":" in txt else txt

        # School District
        if any(k in heading for k in ["school district", "school zones", "schools", "school"]):
            a = section.find("a")
            if a and not result["school_district"]:
                candidate = _clean_text(a.get_text())
                if len(candidate) >= 4:
                    result["school_district"] = candidate

            # sometimes district appears as plain text in list items
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
        # Use session for connection pooling (faster)
        session = requests.Session()
        r = session.get(
            LOOKUP_URL,
            params={"addr": address},
            headers=HEADERS,
            timeout=10,  # Reduced from 20 to 10 seconds
            allow_redirects=True,
        )
        if r.status_code != 200:
            return None

        html = r.text
        # Only parse if expected structure is present
        if "halfcontentpadded" not in html.lower():
            return None

        parsed = _parse_address_page(html)
        if parsed.get("township") or parsed.get("school_district"):
            return parsed
        return None
    except Exception:
        return None


def _driver_path_local() -> str:
    """
    Use msedgedriver.exe stored in the same folder as this file.
    """
    here = os.path.dirname(__file__)
    driver_path = os.path.join(here, "msedgedriver.exe")
    return driver_path


def _create_edge_driver(headless: bool = True) -> Tuple[webdriver.Edge, str]:
    """
    Create Edge driver with a unique user-data-dir (avoids profile locking).
    Returns (driver, temp_user_data_dir).
    """
    opts = EdgeOptions()
    opts.use_chromium = True

    if headless:
        opts.add_argument("--headless=new")

    # Performance optimizations - disable unnecessary features
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--log-level=3")
    
    # Speed optimizations - disable images to load faster
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Block images
        "profile.default_content_setting_values.notifications": 2,
    }
    opts.add_experimental_option("prefs", prefs)
    opts.add_argument("--blink-settings=imagesEnabled=false")

    # unique profile dir so you don’t get "user data dir already in use"
    tmp_ud = tempfile.mkdtemp(prefix="edgedata_")
    opts.add_argument(f"--user-data-dir={tmp_ud}")

    driver_path = _driver_path_local()
    if not os.path.exists(driver_path):
        raise FileNotFoundError(
            f"msedgedriver.exe not found at: {driver_path}\n"
            "Put msedgedriver.exe in the same folder as selenium_scraper.py"
        )

    service = EdgeService(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=opts)
    driver.set_page_load_timeout(20)  # Reduced from 40 to 20 seconds
    driver.set_window_size(1200, 900)
    
    # Set script timeout for faster failure
    driver.set_script_timeout(10)

    return driver, tmp_ud


# Cache for address lookups (in-memory, persists for session)
_address_cache: Dict[str, dict] = {}

def get_township_school_from_address(address: str, headless: bool = True) -> dict:
    """
    Return {township, county, school_district} for an address.
    Fast path first; fallback to Selenium if needed.
    Uses caching to avoid repeated lookups for the same address.
    """
    # Normalize address for cache key
    cache_key = address.strip().lower()
    
    # Check cache first
    if cache_key in _address_cache:
        return _address_cache[cache_key]

    # ---- FAST PATH (no browser) ----
    fast = _try_fast_lookup(address)
    if fast:
        # Cache successful fast lookup
        _address_cache[cache_key] = fast
        return fast

    # ---- SELENIUM FALLBACK ----
    driver = None
    tmp_ud = None

    try:
        driver, tmp_ud = _create_edge_driver(headless=headless)
        wait = WebDriverWait(driver, 15)  # Reduced from 25 to 15 seconds

        # Use shorter timeout for initial page load
        driver.get(HTL_HOME)

        # Wait for search box with shorter timeout
        search = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".address_input.localsearchmapfield"))
        )
        search.clear()
        search.send_keys(address)
        search.send_keys(Keys.RETURN)

        # If results list appears, click first result (shorter timeout)
        try:
            first = WebDriverWait(driver, 3).until(  # Reduced timeout
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.list-group a"))
            )
            first.click()
        except Exception:
            pass

        # Wait for page content with shorter timeout
        WebDriverWait(driver, 10).until(  # Reduced from 25 to 10 seconds
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
