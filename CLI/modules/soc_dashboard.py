import sqlite3
import os
import time
import csv
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live

DB_PATH = "DATABASE/aegis_advanced_structured.db"
AUDIT_LOG = "system_audit.log"
console = Console()


def fetch_alerts(resolved=None, severity=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, timestamp, severity, source, description, resolved FROM alerts"
    params = []
    if resolved is not None or severity:
        query += " WHERE"
        if resolved is not None:
            query += " resolved = ?"
            params.append(1 if resolved else 0)
        if severity:
            if resolved is not None:
                query += " AND"
            query += " severity = ?"
            params.append(severity)
    query += " ORDER BY timestamp DESC LIMIT 20"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows


def display_alerts(alerts):
    table = Table(title="📡 SOC Alert Center")
    table.add_column("ID", style="bold")
    table.add_column("Time", style="dim")
    table.add_column("Severity")
    table.add_column("Source")
    table.add_column("Description")
    table.add_column("Status")
    for alert in alerts:
        table.add_row(
            str(alert[0]), alert[1], alert[2], alert[3], alert[4],
            "✅" if alert[5] else "❌")
    console.print(table)


def mark_resolved(alert_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] ALERT {alert_id} marked as resolved.\n")
    console.print(f"[green]✔ Alert {alert_id} marked as resolved.[/green]")


def export_alerts_csv():
    alerts = fetch_alerts()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"alerts_export_{ts}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Time", "Severity", "Source", "Description", "Resolved"])
        for alert in alerts:
            writer.writerow(alert)
    console.print(f"[green]✔ Exported to {filename}[/green]")


def tail_audit_log(lines=10):
    if not os.path.exists(AUDIT_LOG):
        console.print("[dim]No audit log found.[/dim]")
        return
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        log_lines = f.readlines()[-lines:]
    console.print("[bold]🧾 Audit Trail:[/bold]")
    for line in log_lines:
        console.print(f"[dim]{line.strip()}[/dim]")


def soc_dashboard_menu():
    while True:
        console.print("\n[bold cyan]SOC Analyst Dashboard[/bold cyan]")
        console.print("[1] View Active Alerts")
        console.print("[2] View Resolved Alerts")
        console.print("[3] View Critical Only")
        console.print("[4] Mark Alert as Resolved")
        console.print("[5] Export Alerts to CSV")
        console.print("[6] View Audit Trail")
        console.print("[7] Watch Mode (Live Refresh)")
        console.print("[0] Exit")
        choice = Prompt.ask("Choose option", choices=["1","2","3","4","5","6","7","0"])

        if choice == "1":
            alerts = fetch_alerts(resolved=False)
            display_alerts(alerts)
        elif choice == "2":
            alerts = fetch_alerts(resolved=True)
            display_alerts(alerts)
        elif choice == "3":
            alerts = fetch_alerts(resolved=False, severity="critical")
            display_alerts(alerts)
        elif choice == "4":
            alert_id = Prompt.ask("Enter Alert ID to resolve")
            mark_resolved(alert_id)
        elif choice == "5":
            export_alerts_csv()
        elif choice == "6":
            tail_audit_log()
        elif choice == "7":
            console.print("[cyan]🔄 Entering watch mode. Press Ctrl+C to exit.[/cyan]")
            try:
                with Live(refresh_per_second=1) as live:
                    while True:
                        alerts = fetch_alerts(resolved=False)
                        table = Table(title="[bold red]Live Alerts Monitor")
                        table.add_column("ID")
                        table.add_column("Time")
                        table.add_column("Severity")
                        table.add_column("Source")
                        table.add_column("Description")
                        for a in alerts:
                            table.add_row(str(a[0]), a[1], a[2], a[3], a[4])
                        live.update(table)
                        time.sleep(3)
            except KeyboardInterrupt:
                console.print("[yellow]Exited watch mode.[/yellow]")
        elif choice == "0":
            break
