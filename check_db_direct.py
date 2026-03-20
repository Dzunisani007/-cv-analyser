import sqlite3
import json

print("=== Direct Database Check ===")

conn = sqlite3.connect('cv_analyser_test.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Check cv_records
cursor.execute("SELECT COUNT(*) FROM cv_records")
count = cursor.fetchone()[0]
print(f"\nCV Records count: {count}")

# Check cv_analyses
cursor.execute("SELECT id, status, warnings FROM cv_analyses ORDER BY created_at DESC LIMIT 5")
analyses = cursor.fetchall()
print(f"\nRecent analyses:")
for analysis in analyses:
    print(f"  ID: {analysis[0][:8]}..., Status: {analysis[1]}, Warnings: {analysis[2]}")

conn.close()
