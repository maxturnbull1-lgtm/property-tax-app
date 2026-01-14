import re
import sqlite3
import streamlit as st
import pandas as pd

from fuzzywuzzy import fuzz
import os

# Use cloud scraper if in cloud environment (Koyeb, Streamlit Cloud, etc.)
IS_CLOUD = (
    os.environ.get("PORT") is not None or  # Koyeb, Heroku, etc.
    os.environ.get("STREAMLIT_SERVER_PORT") is not None or  # Streamlit Cloud
    os.environ.get("KOYEB_APP_NAME") is not None  # Koyeb specific
)

if IS_CLOUD:
    from cloud_scraper import get_township_school_from_address
else:
    from selenium_scraper import get_township_school_from_address

DB_PATH = "all_millage_rates.db"
TABLE_NAME = "millage"


# ----------------- Text cleaning -----------------
def clean_city_twp(s: str) -> str:
    s = (s or "").strip().lower()
    junk = [
        "city of", "village of", "charter township of", "charter township",
        "township of", "township", "twp", "city", "village"
    ]
    for j in junk:
        s = s.replace(j, " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.title()


def clean_school(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.title()


# ----------------- Mortgage Coach helpers -----------------
def scenario_property_name(address: str) -> str:
    # "4524 Glory Way SW, Wyoming, MI 49418" -> "4524 Glory Way SW"
    if not address:
        return ""
    first_part = address.split(",")[0].strip()
    first_part = re.sub(r"\s+", " ", first_part)
    return first_part


def format_k(price: float) -> str:
    # 155000 -> $155K
    k = int(round(price / 1000.0))
    return f"${k:,}K"


def build_scenario_name(address: str, price: float) -> str:
    prop = scenario_property_name(address)
    val = format_k(price)
    if not prop:
        return val
    return f"{prop} - {val}"


def money_number_only(x: float) -> str:
    # 750.28 -> "750.28" (no $ no commas)
    return f"{x:.2f}"


# ----------------- Load millage data -----------------
@st.cache_data
def load_millage_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()

    required = [
        "Township/City",
        "School District",
        "Total Homestead Millage Rate",
        "Total Non-Homestead Millage Rate",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"DB table is missing columns: {missing}")

    df["Township_Clean"] = df["Township/City"].apply(clean_city_twp)
    df["School_Clean"] = df["School District"].apply(clean_school)
    df["Combined_Clean"] = df["Township_Clean"] + " - " + df["School_Clean"]

    df["Combined Key"] = df["Township/City"].astype(str) + " - " + df["School District"].astype(str)
    return df


def find_top_matches(df: pd.DataFrame, township: str, school: str, top_n: int = 8):
    t = clean_city_twp(township)
    s = clean_school(school)
    target = f"{t} - {s}"

    scores = []
    for _, row in df.iterrows():
        cand = row["Combined_Clean"]
        score = fuzz.token_set_ratio(target, cand)
        scores.append(score)

    out = df.copy()
    out["Score"] = scores
    out = out.sort_values("Score", ascending=False).head(top_n).reset_index(drop=True)
    return target, out


def calc_taxes(price: float, millage_rate_mills: float):
    assessed = price * 0.45
    annual = assessed * (millage_rate_mills / 1000.0)
    monthly = annual / 12.0
    return assessed, annual, monthly


# ----------------- UI -----------------
st.set_page_config(page_title="Michigan Property Tax Estimator", layout="centered")
st.title("🏠 Michigan Property Tax Estimator")

HEADLESS = True

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

try:
    millage_df = load_millage_data()
except Exception as e:
    st.error(f"Could not load millage database: {e}")
    st.stop()

st.markdown("### Inputs")
address = st.text_input(
    "Property Address",
    placeholder="e.g. 4524 Glory Way SW, Wyoming, MI 49418"
)
price = st.number_input("Property Value ($)", min_value=10000, step=1000, format="%d")
tax_type = st.radio("Tax Type", ["Homestead", "Non-Homestead"], horizontal=True)

if st.button("Estimate Taxes"):
    if not address.strip() or not price:
        st.warning("Please enter both the address and property value.")
        st.stop()

    scraped = get_township_school_from_address(address.strip(), headless=HEADLESS)

    if isinstance(scraped, dict) and "error" in scraped:
        st.error(f"⚠️ {scraped['error']}")
        st.info("💡 **Tip**: The fast lookup method failed. You can try entering the address again, or the system will attempt to use the browser-based scraper.")
        
        # Show a retry button
        if st.button("🔄 Try Again"):
            st.rerun()
        st.stop()

    township_raw = (scraped.get("township") or "").strip()
    school_raw = (scraped.get("school_district") or scraped.get("school") or "").strip()
    county_raw = (scraped.get("county") or "").strip()

    if not township_raw or not school_raw:
        st.error("Could not extract township and/or school district from that address.")
        st.stop()

    target_key, top = find_top_matches(millage_df, township_raw, school_raw, top_n=8)

    st.subheader("📍 Best matches (pick the correct one)")
    options = [f"{row['Combined Key']}   (Score: {row['Score']})" for _, row in top.iterrows()]
    chosen = st.selectbox("Select match", options, index=0)

    row = top.iloc[options.index(chosen)]

    millage_rate = float(row["Total Homestead Millage Rate"]) if tax_type == "Homestead" else float(row["Total Non-Homestead Millage Rate"])
    assessed, annual, monthly = calc_taxes(price, millage_rate)

    st.session_state["last_result"] = {
        "address": address.strip(),
        "price": float(price),
        "tax_type": tax_type,
        "county": county_raw,
        "matched_key": row["Combined Key"],
        "match_score": int(row["Score"]),
        "millage_rate": float(millage_rate),
        "assessed": float(assessed),
        "annual": float(annual),
        "monthly": float(monthly),
    }

# ----------------- Results -----------------
if st.session_state["last_result"]:
    r = st.session_state["last_result"]

    st.subheader("📊 Tax Estimate")
    if r["county"]:
        st.write(f"**County:** {r['county']}")
    st.write(f"**Matched:** {r['matched_key']}")
    st.write(f"**Match score:** {r['match_score']}")
    st.write(f"**Millage rate (mills):** {r['millage_rate']}")
    st.write(f"**Assessed value (45%):** ${r['assessed']:,.2f}")
    st.write(f"**Annual tax:** ${r['annual']:,.2f}")

    # Monthly + copy button (numbers only)
    monthly_num = money_number_only(r["monthly"])
    row1, row2 = st.columns([2, 1])
    with row1:
        st.write(f"**Monthly tax:** ${r['monthly']:,.2f}")
    with row2:
        st.code(monthly_num)

    # Copy button using a tiny JS snippet
    st.components.v1.html(
        f"""
        <div style="margin-top:-6px;">
          <button id="copyMonthly"
            style="
              padding:8px 12px;
              border-radius:8px;
              border:1px solid #ddd;
              cursor:pointer;
              font-weight:600;">
            Copy monthly taxes
          </button>
          <span id="copystatus" style="margin-left:10px; font-size:13px;"></span>
        </div>

        <script>
          const txt = "{monthly_num}";
          const btn = document.getElementById("copyMonthly");
          const status = document.getElementById("copystatus");

          btn.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText(txt);
              status.textContent = "Copied!";
              setTimeout(() => status.textContent = "", 1200);
            }} catch (e) {{
              status.textContent = "Copy failed";
              setTimeout(() => status.textContent = "", 1200);
            }}
          }});
        </script>
        """,
        height=60,
    )

    # Mortgage Coach helper (only scenario name + link)
    st.markdown("---")
    st.subheader("🏦 Mortgage Coach")
    scenario_name = f"{build_scenario_name(r['address'], r['price'])} - % Down - 1 Point"
    st.write("**Scenario Name:**")
    st.code(scenario_name)
    st.link_button("Open Mortgage Coach", "https://edge.mortgagecoach.com/mc-editor/#/client")
