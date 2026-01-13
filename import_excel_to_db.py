import pandas as pd
import sqlite3

# Load your cleaned Excel file
excel_file = "All_Millage_Rates.xlsx"
df = pd.read_excel(excel_file)

# Connect to SQLite (creates a new file if it doesn't exist)
conn = sqlite3.connect("all_millage_rates.db")

# Save the DataFrame as a table named 'millage'
df.to_sql("millage", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("✅ Excel converted to SQLite database (all_millage_rates.db)")
