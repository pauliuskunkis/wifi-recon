#!/usr/bin/env python3
# reads and prints everything stored in captures.db
import sqlite3

conn = sqlite3.connect("captures.db")
cur = conn.cursor()

# SELECT = ask the database for data. * means "all columns"
cur.execute("SELECT * FROM networks")

# fetchall() returns every matching row as a list
rows = cur.fetchall()

print(f"Total rows in database: {len(rows)}")
for row in rows:
    print(row)

conn.close()
