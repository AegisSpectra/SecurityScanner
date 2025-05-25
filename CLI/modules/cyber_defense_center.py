import os
import sqlite3
import hashlib
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from SCANNER.scanner import quick_scan, full_scan, hybrid_scan
from core.export_pdf import export_log_to_pdf
from core.rust_bridge import get_risk_score
import psutil

DB_PATH = "DATABASE/aegis_advanced_structured.db"
console = Console()

def calculate_current_risk():
    cpu = int(psutil.cpu_percent(interval=1))
    ram = int(psutil.virtual_memory().percent)
    net = int(psutil.net_io_counters().bytes_sent / 1024 / 1024) % 100
    score = get_risk_score(cpu, ram, net)
    return cpu, ram, net, score

def trigger_auto_response(score):
    if score > 85:
        console.print("[bold red]⚠ High Risk Detected! Initiating auto-quarantine...[/bold red]")
        path = "C:/Suspicious/example_file.exe"  # Placeholder
        simulate_quarantine(path)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alerts (timestamp, type, severity, source, description, resolved) VALUES (?, ?, ?, ?, ?, ?)", 
            (datetime.now().isoformat(), "auto", "critical", path, f"Auto-quarantine triggered due to risk score {score}", 0))
        conn.commit()
        conn.close()
        console.print("[red]Auto alert added to database.[/red]")

def show_risk_analysis():
    cpu, ram, net, score = calculate_current_risk()
    console.print(f"[cyan]CPU Usage:[/] {cpu}%")
    console.print(f"[cyan]RAM Usage:[/] {ram}%")
    console.print(f"[cyan]Network Sent (mocked):[/] {net} MB")
    console.print(f"[bold red]🔥 RISK SCORE:[/] {score}")
    trigger_auto_response(score)
    console.input("\nPress Enter to continue...")

def calculate_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def scan_entire_disk():
    suspicious = []
    suspicious_ext = ['.exe', '.dll', '.bat', '.scr', '.vbs', '.js', '.ps1']
    root = "C:\\" if os.name == "nt" else "/"

    console.print(f"[cyan]Scanning entire disk from {root}...[/cyan]")
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            if os.path.splitext(file)[1].lower() in suspicious_ext:
                suspicious.append(filepath)

    if not suspicious:
        console.print("[green]No suspicious files found.[/green]")
    else:
        console.print(f"[bold red]Suspicious files found: {len(suspicious)}[/bold red]")
        for path in suspicious[:10]:
            console.print(f"• {path}")
        console.print("[yellow]...more not shown[/yellow]" if len(suspicious) > 10 else "")

    console.input("\nPress Enter to continue...")

def vt_check_hash():
    file_path = Prompt.ask("Enter full file path")
    if not os.path.exists(file_path):
        console.print("[red]File does not exist.[/red]")
        return
    hash_val = calculate_file_hash(file_path)
    console.print(f"[cyan]Simulated VT check for hash:[/] {hash_val}")
    console.input("\nPress Enter to continue...")

def mark_file_suspicious():
    path = Prompt.ask("Enter full path to suspicious file")
    reason = Prompt.ask("Why is it suspicious?")
    severity = Prompt.ask("Severity", choices=["low", "medium", "high", "critical"], default="high")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alerts (timestamp, type, severity, source, description, resolved) VALUES (?, ?, ?, ?, ?, ?)", 
                   (datetime.now().isoformat(), "manual", severity, path, reason, 0))
    conn.commit()
    conn.close()

    console.print("[red]File marked as suspicious and added to alerts.[/red]")
    console.input("\nPress Enter to continue...")

def simulate_quarantine(path):
    console.print(f"[yellow]Simulating quarantine of: {path}[/yellow]")
    console.input("\nPress Enter to continue...")

def rule_engine_preview():
    console.print("[cyan]Coming soon: AI Rule Engine[/cyan]")
    console.print("- IF process = 'powershell.exe' AND RAM > 80% THEN ALERT")
    console.print("- IF file = '*.bat' AND user != admin THEN QUARANTINE")
    console.input("\nPress Enter to continue...")

def cyber_defense_menu(username, role):
    while True:
        console.print("\n[bold magenta]Cyber Defense Center[/bold magenta]")
        console.print("[1] Run Quick Scan")
        console.print("[2] Run Full Scan")
        console.print("[3] Run Hybrid Scan")
        console.print("[4] Check File Hash with VirusTotal")
        console.print("[5] Mark File as Suspicious")
        console.print("[6] Simulated Quarantine")
        console.print("[7] Apply Rule Engine (preview)")
        console.print("[8] Scan Entire Disk for Suspicious Files")
        console.print("[9] Show System Risk Score (via Rust)")
        console.print("[0] Back")

        choice = Prompt.ask("Select an option", choices=[str(i) for i in range(10)], default="0")

        if choice == "1":
            quick_scan(username, role)
        elif choice == "2":
            directory = Prompt.ask("Enter directory to scan", default="/")
            full_scan(directory, role)
        elif choice == "3":
            hybrid_scan(username, role)
        elif choice == "4":
            vt_check_hash()
        elif choice == "5":
            mark_file_suspicious()
        elif choice == "6":
            simulate_quarantine("User-requested file")
        elif choice == "7":
            rule_engine_preview()
        elif choice == "8":
            scan_entire_disk()
        elif choice == "9":
            show_risk_analysis()
        elif choice == "0":
            break