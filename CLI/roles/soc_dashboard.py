# CLI/roles/soc_dashboard.py
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
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


def soc_dashboard_menu(username):
    console.clear()
    console.print(f"[bold green]Welcome {username} to the SOC Analyst Dashboard[/bold green]\n")

    while True:
        console.print("[1] 🔔 View Alerts")
        console.print("[2] 🧠 Analyze Threats")
        console.print("[3] 📜 View Logs")
        console.print("[0] ❌ Exit")

        choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3"])

        if choice == "1":
            console.print("[yellow]🔔 Live alerts will appear here (feature in progress).[/yellow]")
        elif choice == "2":
            console.print("[cyan]🧠 Threat intelligence analysis placeholder.[/cyan]")
        elif choice == "3":
            console.print("[dim]📜 SOC logs loading... (future logs feature)[/dim]")
        elif choice == "0":
            break

        console.input("\n[white]Press Enter to return to menu...[/white]")
