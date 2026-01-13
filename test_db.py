import pandas as pd
import sqlite3

conn = sqlite3.connect("millage_rates.db")
df = pd.read_sql_query("SELECT * FROM millage", conn)
conn.close()

print(df)

