from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

def scrape_from_full_address(address):
    print(f"🔍 Scraping: {address}")
    search_url = f"https://michigan.hometownlocator.com/maps/address-lookup.cfm?addr={quote_plus(address)}"
    print(f"📡 URL: {search_url}")

    try:
        response = requests.get(search_url)
        print(f"📥 Status Code: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        data = {
            "county": "",
            "township": "",
            "school_district": ""
        }
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                print(f"🔎 Found: {label} -> {value}")
                if "county" in label:
                    data["county"] = value
                elif "township" in label:
                    data["township"] = value
                elif "school district" in label:
                    data["school_district"] = value
        return data
    except Exception as e:
        return {"error": str(e)}

# Test it
result = scrape_from_full_address("4524 Glory Way SW, Wyoming, MI 49418")
print("✅ FINAL RESULT:")
print(result)
