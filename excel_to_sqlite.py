import pandas as pd
import sqlite3

# Load your cleaned Excel file
excel_file = "Millage_Rates.xlsx"
df = pd.read_excel(excel_file)

# Connect to SQLite (creates a new file if it doesn't exist)
conn = sqlite3.connect("millage_rates.db")

# Save the DataFrame as a table named 'millage'
df.to_sql("millage", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("✅ Excel converted to SQLite database (millage_rates.db)")
