import sqlite3
import hashlib
import csv
import getpass
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from datetime import datetime

DB_PATH = "DATABASE/aegis_advanced_structured.db"
console = Console()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def view_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, email, company_id, status FROM users")
    users = cursor.fetchall()
    conn.close()

    table = Table(title="All Users", header_style="bold cyan")
    table.add_column("Username", style="bold")
    table.add_column("Role")
    table.add_column("Email")
    table.add_column("Company ID")
    table.add_column("Status")

    for user in users:
        table.add_row(*[str(i or "-") for i in user])

    console.print(table)

def search_users():
    console.print("[bold green]Search Users[/bold green]")
    console.print("Search by:\n[1] Username\n[2] Role\n[3] User ID\n[4] Company ID\n[5] Company Name\n[0] Back")
    option = Prompt.ask("Choose search option", choices=["0", "1", "2", "3", "4", "5"], default="0")

    field_map = {
        "1": ("username", "Username"),
        "2": ("role", "Role"),
        "3": ("rowid", "User ID"),
        "4": ("company_id", "Company ID")
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if option in field_map:
        field, label = field_map[option]
        value = Prompt.ask(f"Enter {label}")
        cursor.execute(f"SELECT rowid, username, role, email, company_id, status FROM users WHERE {field} LIKE ?", ('%' + value + '%',))
    elif option == "5":
        name = Prompt.ask("Enter Company Name")
        cursor.execute("""
            SELECT u.rowid, u.username, u.role, u.email, u.company_id, u.status
            FROM users u
            JOIN companies c ON u.company_id = c.company_id
            WHERE c.name LIKE ?
        """, ('%' + name + '%',))
    else:
        return

    results = cursor.fetchall()
    if not results:
        console.print("[red]No users found.[/red]")
        conn.close()
        return

    table = Table(title="Search Results", show_header=True, header_style="bold cyan")
    table.add_column("ID")
    table.add_column("Username")
    table.add_column("Role")
    table.add_column("Email")
    table.add_column("Company ID")
    table.add_column("Status")

    for row in results:
        table.add_row(*[str(i or "-") for i in row])

    console.print(table)
    uid = Prompt.ask("Enter ID to manage specific user, or 0 to cancel", default="0")

    if uid != "0":
        manage_user(uid)

    conn.close()

def manage_user(uid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, email, company_id, status FROM users WHERE rowid=?", (uid,))
    user = cursor.fetchone()
    if not user:
        console.print("[red]User not found.[/red]")
        return

    username, role, email, company_id, status = user
    console.print(f"Managing user: [bold cyan]{username}[/bold cyan] ({role})\n")

    console.print("[1] Edit Role")
    console.print("[2] Edit Email")
    console.print("[3] Edit Company ID")
    console.print("[4] Change Username")
    console.print("[5] Reset Password")
    console.print("[6] Change Status")
    console.print("[7] Delete User")
    console.print("[0] Back")

    choice = Prompt.ask("Choose action", choices=[str(i) for i in range(8)], default="0")

    if choice == "1":
        new_role = Prompt.ask("Enter new role")
        cursor.execute("UPDATE users SET role=? WHERE rowid=?", (new_role, uid))
    elif choice == "2":
        new_email = Prompt.ask("Enter new email")
        cursor.execute("UPDATE users SET email=? WHERE rowid=?", (new_email, uid))
    elif choice == "3":
        new_company = Prompt.ask("Enter new company ID")
        cursor.execute("UPDATE users SET company_id=? WHERE rowid=?", (new_company, uid))
    elif choice == "4":
        new_user = Prompt.ask("Enter new username")
        cursor.execute("UPDATE users SET username=? WHERE rowid=?", (new_user, uid))
    elif choice == "5":
        new_pass = getpass.getpass("Enter new password: ")
        hashed = hash_password(new_pass)
        cursor.execute("UPDATE users SET password=? WHERE rowid=?", (hashed, uid))
    elif choice == "6":
        new_status = Prompt.ask("Enter status (active/suspended/deleted)", default="active")
        cursor.execute("UPDATE users SET status=? WHERE rowid=?", (new_status, uid))
    elif choice == "7":
        confirm = Confirm.ask("Are you sure you want to delete this user?")
        if confirm:
            cursor.execute("DELETE FROM users WHERE rowid=?", (uid,))
            console.print("[green]User deleted.[/green]")
            conn.commit()
            conn.close()
            return

    conn.commit()
    conn.close()
    console.print("[green]Update complete.[/green]")

def add_user():
    console.print("[cyan]Adding New User[/cyan]")
    username = Prompt.ask("Enter username")
    raw_password = getpass.getpass("Enter password: ")
    password = hash_password(raw_password)
    role = Prompt.ask("Role", choices=["super_admin", "client_private", "client_business", "soc"])
    email = Prompt.ask("Email")
    company_id = Prompt.ask("Company ID")
    status = Prompt.ask("Status", choices=["active", "inactive"], default="active")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role, email, company_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                           (username, password, role, email, company_id, status))
            conn.commit()
            console.print("[green]✔ User added successfully.[/green]")
    except sqlite3.Error as e:
        console.print(f"[red]Database error:[/] {e}")

def export_users_to_csv():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, email, company_id, status FROM users")
    users = cursor.fetchall()
    conn.close()

    with open("exported_users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Username", "Role", "Email", "Company ID", "Status"])
        writer.writerows(users)

    console.print("[green]Exported to exported_users.csv[/green]")

def user_management_menu():
    while True:
        console.print("\n[bold cyan]User & Role Management[/bold cyan]")
        console.print("[1] View Users")
        console.print("[2] Add User")
        console.print("[3] Delete User")
        console.print("[4] Search Users")
        console.print("[5] Export to CSV")
        console.print("[0] Back")

        choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5"], default="0")

        if choice == "1":
            view_users()
        elif choice == "2":
            add_user()
        elif choice == "3":
            username = Prompt.ask("Enter username to delete")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            conn.close()
            console.print("[green]User deleted.[/green]")
        elif choice == "4":
            search_users()
        elif choice == "5":
            export_users_to_csv()
        elif choice == "0":
            break

        console.input("\nPress Enter to continue...")
