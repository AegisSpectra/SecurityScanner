from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from CLI.modules.system_overview import system_overview
from CLI.modules.user_management import user_management_menu
from CLI.modules.cyber_defense_center import cyber_defense_menu
from CLI.modules.auto_defense import auto_defense_menu
from CLI.modules.soc_dashboard import soc_dashboard_menu
from CLI.modules.system_settings import system_settings_menu
from CLI.modules.debug_tools import debug_tools_menu
from CLI.modules.reports_analytics import reports_menu
from auth import auth_mgr, require_permission, PermissionError

import psutil

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
    
console = Console()


def get_security_score():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    conns = len(psutil.net_connections())
    score = int((cpu * 0.3) + (ram * 0.4) + min(conns / 10, 100) * 0.3)
    status = "🟢 SAFE"
    if score > 70:
        status = "🔴 BREACHED"
    elif score > 40:
        status = "🟡 SUSPICIOUS"
    return f"[dim]Security Status:[/] {status}  |  CPU: {cpu}%  RAM: {ram}%  Connections: {conns}  Score: {score}/100"


def super_admin_cli(username):
    role = "super_admin"

    while True:
        console.clear()
        console.print(Panel(get_security_score(), title="Aegis Live Security Monitor", border_style="cyan"))
        console.print("[bold green]🛡️ Aegis Spectra[/] - Super Admin Panel", style="bold")
        console.print(f"Logged in as: [cyan]{username}[/]\n")
        console.print("[1] System Overview")
        console.print("[2] User & Role Management")
        console.print("[3] SOC Dashboard")
        console.print("[4] Cyber Defense Center")
        console.print("[5] Reports & Analytics")
        console.print("[6] System Settings")
        console.print("[7] Advanced Security")
        console.print("[8] Developer/Debug Zone")
        console.print("[D] Auto Defense")
        console.print("[0] Exit\n")

        choice = Prompt.ask("[bold yellow]Select an option:[/]", default="0")

        if choice == "1":
            system_overview()
        elif choice == "2":
            user_management_menu()
        elif choice == "3":
            soc_dashboard_menu()
        elif choice == "4":
            cyber_defense_menu(username, role)
        elif choice == "5":
            reports_menu()
        elif choice == "6":
            system_settings_menu()
        elif choice == "7":
            console.print("[cyan]🔐 Loading Advanced Security Module...[/]")
        elif choice == "8":
             debug_tools_menu()
        elif choice.upper() == "D":
            auto_defense_menu()
        elif choice == "0":
            console.print("[green]✔ Exiting Super Admin Panel. Goodbye![/]")
            break

        console.input("\n[bold white]Press Enter to return to main menu...[/]")
