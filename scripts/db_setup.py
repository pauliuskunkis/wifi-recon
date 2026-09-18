#!/usr/bin/env python3
# creates SQLite Base and table to store beacons
import sqlite3          # Python imports SQLite 

# open or create file if it doesn't exist
conn = sqlite3.connect("captures.db")

# cursor - will be used to send signals
cur = conn.cursor()

# SQL command to create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS networks (
        timestamp TEXT,
        bssid TEXT,
        ssid TEXT,
        signal INTEGER
    )
""")

conn.commit()    # confirm changes & save
conn.close()     # closes
print("Table has been created.")
