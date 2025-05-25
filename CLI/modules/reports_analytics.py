import os
import glob
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
import webbrowser
import platform

REPORTS_DIR = "REPORTS"
console = Console()

def list_reports():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    files = glob.glob(os.path.join(REPORTS_DIR, "*.pdf")) + glob.glob(os.path.join(REPORTS_DIR, "*.html"))
    return sorted(files, key=os.path.getmtime, reverse=True)

def view_reports_table(reports=None):
    if reports is None:
        reports = list_reports()
    if not reports:
        console.print("[dim]No reports found.[/dim]")
        return
    table = Table(title="📊 Available Reports")
    table.add_column("#", justify="right")
    table.add_column("Filename")
    table.add_column("Last Modified")
    for i, file in enumerate(reports, 1):
        mtime = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
        table.add_row(str(i), os.path.basename(file), mtime)
    console.print(table)
    return reports

def filter_by_type(extension):
    reports = list_reports()
    return [r for r in reports if r.endswith(extension)]

def filter_by_date_range(start_date, end_date):
    reports = list_reports()
    results = []
    for file in reports:
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        if start_date <= mtime <= end_date:
            results.append(file)
    return results

def open_report_cross_platform(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        os.system(f"open '{filepath}'")
    else:
        os.system(f"xdg-open '{filepath}'")

def generate_summary_report():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(REPORTS_DIR, f"summary_report_{timestamp}.txt")
    with open(filename, "w") as f:
        f.write("Summary Report\n")
        f.write(f"Generated at: {datetime.now()}\n")
        f.write("\n[Sample Summary Content]\n")
    console.print(f"[green]✔ Summary report generated:[/] {filename}")


def reports_menu():
    while True:
        console.clear()
        console.print("[bold cyan]Reports & Analytics[/bold cyan]")
        console.print("[1] View Available Reports")
        console.print("[2] Open Report")
        console.print("[3] Delete Report")
        console.print("[4] Filter by Type")
        console.print("[5] Filter by Date Range")
        console.print("[6] Generate Summary Report")
        console.print("[0] Back")
        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "0"])

        if choice == "1":
            view_reports_table()
            console.input("Press Enter to return...")

        elif choice == "2":
            reports = view_reports_table()
            if not reports:
                console.input("No reports found. Press Enter...")
                continue
            num = Prompt.ask("Enter report # to open", default="1")
            try:
                index = int(num) - 1
                if 0 <= index < len(reports):
                    open_report_cross_platform(reports[index])
                    console.print("[green]✔ Report opened[/green]")
                else:
                    console.print("[red]Invalid report number.[/red]")
            except ValueError:
                console.print("[red]Invalid input.[/red]")
            console.input("Press Enter to continue...")

        elif choice == "3":
            reports = view_reports_table()
            if not reports:
                console.input("No reports found. Press Enter...")
                continue
            num = Prompt.ask("Enter report # to delete", default="1")
            try:
                index = int(num) - 1
                if 0 <= index < len(reports):
                    os.remove(reports[index])
                    console.print("[red]✖ Report deleted[/red]")
                else:
                    console.print("[red]Invalid report number.[/red]")
            except ValueError:
                console.print("[red]Invalid input.[/red]")
            console.input("Press Enter to continue...")

        elif choice == "4":
            ext = Prompt.ask("Enter file type (e.g. .pdf, .html)", default=".pdf")
            filtered = filter_by_type(ext)
            view_reports_table(filtered)
            console.input("Press Enter to return...")

        elif choice == "5":
            try:
                start = Prompt.ask("Enter start date (YYYY-MM-DD)")
                end = Prompt.ask("Enter end date (YYYY-MM-DD)")
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
                filtered = filter_by_date_range(start_date, end_date)
                view_reports_table(filtered)
            except Exception as e:
                console.print(f"[red]Invalid date format: {e}[/red]")
            console.input("Press Enter to return...")

        elif choice == "6":
            generate_summary_report()
            console.input("Press Enter to continue...")

        elif choice == "0":
            break
