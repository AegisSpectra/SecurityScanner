from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
import psutil
import threading
import time
import random
import os
import socket

console = Console()
AUTODEFENSE_ACTIVE = False
THREAT_HISTORY = []
BLOCKED_IPS = set()

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
    return score, status, cpu, ram, conns

def log_threat(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    THREAT_HISTORY.append((timestamp, event))
    with open("system_audit.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event}\n")

def simulate_ai_decision(score):
    decision = "ALLOW"
    if score > 80:
        decision = "BLOCK"
    return decision

def block_ip(ip):
    BLOCKED_IPS.add(ip)
    log_threat(f"Blocked IP: {ip}")
    console.print(f"[red]Blocked suspicious IP: {ip}[/red]")

def scan_open_ports():
    open_ports = []
    for port in [21, 22, 23, 80, 443, 445, 3389, 8000, 8080]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex(("127.0.0.1", port))
            if result == 0:
                open_ports.append(port)
    if open_ports:
        log_threat(f"Open ports: {', '.join(map(str, open_ports))}")
    return open_ports

def auto_defense_engine():
    global AUTODEFENSE_ACTIVE
    console.print("[cyan]🛡️ Auto Defense Engine Activated (Autonomous Mode)...[/cyan]")
    while AUTODEFENSE_ACTIVE:
        score, status, cpu, ram, conns = get_security_score()
        if score > 80:
            event = f"High risk score: {score}/100 | CPU: {cpu}% | RAM: {ram}% | Connections: {conns}"
            log_threat(event)
            console.print(f"[red]⚠ {event}[/red]")
            decision = simulate_ai_decision(score)
            if decision == "BLOCK":
                block_ip("192.168.1.100")
        time.sleep(5)

def view_threat_history():
    table = Table(title="📜 System Threat History")
    table.add_column("Time")
    table.add_column("Event")
    for row in THREAT_HISTORY[-10:]:
        table.add_row(row[0], row[1])
    console.print(table)

def auto_defense_menu():
    global AUTODEFENSE_ACTIVE
    while True:
        score, status, cpu, ram, conns = get_security_score()
        console.clear()
        console.print(Panel(f"Status: {status}\nCPU: {cpu}% | RAM: {ram}% | Connections: {conns}\nRisk Score: {score}/100",
                            title="Aegis Auto-Defense Status", border_style="red"))
        console.print("[bold magenta]Auto Defense Menu[/bold magenta]")
        console.print("[1] Activate Autonomous Mode")
        console.print("[2] View Threat History")
        console.print("[3] View Blocked IPs")
        console.print("[4] Scan Open Ports")
        console.print("[5] Deactivate Auto Defense")
        console.print("[0] Back to Main Menu")
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "0"])

        if choice == "1":
            if not AUTODEFENSE_ACTIVE:
                AUTODEFENSE_ACTIVE = True
                threading.Thread(target=auto_defense_engine, daemon=True).start()
                console.print("[green]✔ Defense Engine Running in Background[/green]")
            else:
                console.print("[yellow]Already running[/yellow]")
            time.sleep(2)
        elif choice == "2":
            view_threat_history()
            console.input("Press Enter to return...")
        elif choice == "3":
            console.print("[bold red]Blocked IPs:[/bold red]" if BLOCKED_IPS else "[dim]No IPs blocked yet.[/dim]")
            for ip in BLOCKED_IPS:
                console.print(f"🔒 {ip}")
            console.input("Press Enter to return...")
        elif choice == "4":
            ports = scan_open_ports()
            if ports:
                console.print(f"[yellow]⚠ Open Ports Detected: {ports}[/yellow]")
            else:
                console.print("[green]✔ No common open ports detected[/green]")
            console.input("Press Enter to return...")
        elif choice == "5":
            AUTODEFENSE_ACTIVE = False
            console.print("[red]✖ Defense Engine Deactivated[/red]")
            time.sleep(1)
        elif choice == "0":
            break
