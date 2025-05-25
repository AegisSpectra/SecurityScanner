# CLI/roles/business_client_dashboard.py
from rich.console import Console
from rich.prompt import Prompt
from datetime import datetime
import os
import sqlite3
from auth import auth_mgr, require_permission, PermissionError

console = Console()

def client_dashboard(user_id):
    """
    Main loop for the Private Client dashboard.
    Requires that auth_mgr.load_user(user_id) has been called.
    """
    console.print(f"[bold]Welcome, Private Client (User {user_id})[/bold]\n")

    while True:
        console.print("[underline]Main Menu[/underline]")
        # Show only the options the user has permission for
        menu = {}
        idx = 1
        if auth_mgr.has_permission('scans.view'):
            console.print(f"{idx}. View scan results")
            menu[str(idx)] = view_scans
            idx += 1
        if auth_mgr.has_permission('scans.insert'):
            console.print(f"{idx}. Start quick scan")
            menu[str(idx)] = start_quick_scan
            idx += 1
        if auth_mgr.has_permission('reports.export'):
            console.print(f"{idx}. Export report to PDF")
            menu[str(idx)] = export_report
            idx += 1

        console.print("0. Logout/Exit")
        choice = Prompt.ask("Choose an option", choices=list(menu.keys()) + ["0"])

        if choice == "0":
            console.print("Logging out...\n")
            break

        # Execute the selected action
        action = menu.get(choice)
        try:
            action(user_id)
        except PermissionError as e:
            console.print(f"[red]Access Denied:[/red] {e}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

# ----- Action Functions ----- #

@require_permission('scans.view')
def view_scans(user_id):
    """Display a list of previous scan results."""
    # TODO: Replace with your actual data retrieval logic
    console.print("Showing scan results...")
    # e.g. scan_list = db.get_scans_for_user(user_id)
    # print table

@require_permission('scans.insert')
def start_quick_scan(user_id):
    """Trigger a quick scan for the client."""
    console.print("Starting quick scan...")
    # TODO: call quick_scan function
    # quick_scan(user_id)

@require_permission('reports.export')
def export_report(user_id):
    """Export scan report to a PDF file."""
    console.print("Exporting report to PDF...")
    filename = Prompt.ask("Enter filename", default=f"report_{user_id}.pdf")
    # TODO: call export function, e.g. export_pdf(data, filename)
    console.print(f"Report saved as {filename}")
    
def get_company_name(company_id):
    try:
        conn = sqlite3.connect(r"C:\Users\ilyai\OneDrive\Desktop\Aegis_Spectra_CLI\DATABASE\aegis_advanced_structured.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM companies WHERE company_id = ?", (company_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Unknown Company"
    except Exception as e:
        return f"Error: {e}"
def client_business_dashboard(username, role):
    # שלוף את company_id מהמשתמש
    conn = sqlite3.connect(r"C:\Users\ilyai\OneDrive\Desktop\Aegis_Spectra_CLI\DATABASE\aegis_advanced_structured.db")
    cursor = conn.cursor()
    cursor.execute("SELECT company_id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    company_id = result[0] if result else "UNKNOWN"
    company_name = get_company_name(company_id)

    print(f"[bold blue]Welcome to Aegis for {company_name}[/bold blue]")
    # המשך התפריט...

# === HEADER ===
def render_header():
    console.print("""
[bold blue]
    ____  _ _            _   _                  ____ _ _            _     _             
   |  _ \(_) | ___ _ __| | | |__  _   _ ___   / ___| (_) ___ _ __ | |__ (_)_ __   __ _ 
   | |_) | | |/ _ \ '__| | | '_ \| | | / __| | |   | | |/ _ \ '_ \| '_ \| | '_ \ / _` |
   |  __/| | |  __/ |  | | | |_) | |_| \__ \ | |___| | |  __/ | | | |_) | | | | | (_| |
   |_|   |_|_|\___|_|  |_| |_.__/ \__,_|___/  \____|_|_|\___|_| |_|_.__/|_|_| |_|\__, |
                                                                                |___/ 
[/bold blue]
    """)

# === DASHBOARD ===
def client_business_dashboard(username):
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        render_header()
        console.print(f"[bold green]Logged in as: {username} (client_business)[/bold green]\n")

        console.print("[1] Run Security Scan")
        console.print("[2] View Reports")
        console.print("[3] Company License Info")
        console.print("[4] Submit Support Request")
        console.print("[0] Logout")

        choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"], default="0")

        if choice == "1":
            console.print("[yellow]Scan module will be integrated soon...[/yellow]")
        elif choice == "2":
            console.print("[cyan]Opening report viewer...[/cyan]")
        elif choice == "3":
            console.print("[magenta]License is active until 2025-12-31[/magenta]")
        elif choice == "4":
            console.print("[blue]Support request sent successfully![/blue]")
        elif choice == "0":
            break

        input("\nPress Enter to return to dashboard...")
