# playwright_scraper.py

import sys
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- Windows asyncio fix for Playwright ---
# Streamlit (or other libs) may set a SelectorEventLoop on Windows,
# which does NOT support subprocess -> Playwright breaks with NotImplementedError.
# This forces the Proactor loop that supports subprocess.
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        # If it’s already set or this fails, we just ignore and let Playwright try
        pass


def get_township_school_from_address(address: str) -> dict:
    """
    Uses Playwright (Chromium) to look up an address on
    michigan.hometownlocator.com and extract:
      - township (City/Township/Village)
      - county
      - school_district
    """

    result = {
        "township": None,
        "county": None,
        "school_district": None,
    }

    with sync_playwright() as p:
        # Launch headless Chromium managed by Playwright (no driver path headaches)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1) Go to the main site
            page.goto(
                "https://michigan.hometownlocator.com/",
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # 2) Type address in the search box and submit
            page.fill(".address_input.localsearchmapfield", address)
            page.keyboard.press("Enter")

            # 3) If a result list appears, click the first item; otherwise ignore
            try:
                page.wait_for_selector("div.list-group a", timeout=5000)
                page.click("div.list-group a")
            except Exception:
                # No list -> probably redirected directly; keep going
                pass

            # 4) Wait for the content we care about
            page.wait_for_selector("div.halfcontentpadded", timeout=15000)

            # 5) Grab the HTML and parse with BeautifulSoup
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            for section in soup.find_all("div", class_="halfcontentpadded"):
                h2 = section.find("h2")
                if not h2:
                    continue

                heading = h2.get_text(strip=True).lower()

                # --- Township + County ---
                if "administrative" in heading or "geographic units" in heading:
                    for li in section.find_all("li"):
                        text = li.get_text(" ", strip=True)
                        lower_text = text.lower()

                        if any(
                            x in lower_text
                            for x in ["city of", "township", "village of", "charter township"]
                        ):
                            result["township"] = text

                        if "county" in lower_text:
                            result["county"] = text

                # --- School District ---
                if "school district" in heading or "school zones" in heading:
                    link = section.find("a")
                    if link:
                        result["school_district"] = link.get_text(strip=True)

            return result

        except Exception as e:
            return {"error": str(e)}
        finally:
            browser.close()


# For quick local testing (optional)
if __name__ == "__main__":
    test_address = "4524 Glory Way SW, Wyoming, MI 49418"
    print(get_township_school_from_address(test_address))
