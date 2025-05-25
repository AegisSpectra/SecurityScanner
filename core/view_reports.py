import sqlite3
from datetime import datetime

DB_PATH = "DATABASE/aegis_advanced_structured.db"

def view_reports():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== Report Viewer ===")
    print("1. View by username")
    print("2. View by date (YYYY-MM-DD)")
    print("3. View all")
    print("4. Back")
    choice = input("Choose option: ")

    if choice == "1":
        uname = input("Enter username: ").strip()
        cursor.execute("SELECT * FROM scan_logs WHERE username = ? ORDER BY timestamp DESC", (uname,))
    elif choice == "2":
        date_str = input("Enter date (YYYY-MM-DD): ").strip()
        cursor.execute("SELECT * FROM scan_logs WHERE date(timestamp) = ? ORDER BY timestamp DESC", (date_str,))
    elif choice == "3":
        cursor.execute("SELECT * FROM scan_logs ORDER BY timestamp DESC")
    else:
        conn.close()
        return

    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print("="*60)
            print(f"ID: {row[0]} | User: {row[1]} | Role: {row[2]}")
            print(f"Scan Type: {row[3]} | Time: {row[4]}")
            print("Details:")
            print(row[5])
            print("="*60 + "\n")
    else:
        print("No reports found.")

    conn.close()