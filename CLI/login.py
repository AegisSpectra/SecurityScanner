import sqlite3
import hashlib

DB_PATH = "DATABASE/aegis_advanced_structured.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, hashed))
    result = cursor.fetchone()
    conn.close()

    if result:
        role = result[0]
        print(f"\n[+] Login successful! Welcome, {username} ({role})")
        return username, role
    else:
        print("[-] Login failed.")
        return None, None