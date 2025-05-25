from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime

import os
import json
import webbrowser
import shutil
import threading
import time
import random
import cv2

from SCANNER.scanner import quick_scan, full_scan, hybrid_scan

import pyshark

import tkinter as tk

from tkinter import ttk
from camera.camera_ui import camera_ui_panel

def camera_control_menu():
    camera_ui_panel()

console = Console()
REPORTS_DIR = "REPORTS"
LOG_FILE = "scan_log.txt"
THREATS_FILE = "threats_found.txt"
CAMLOG_FILE = "camlog_logs.txt"
PREFS_FILE = "user_preferences.json"
SCHEDULE_FILE = "scan_schedule.json"
NOTIFICATIONS_FILE = "notifications.json"
FEEDBACK_FILE = "feedbacks.json"
LICENSE_FILE = "license.json"
CONNECTED_USERS_FILE = "connected_users.json"
CAMERA_CONFIG = "camera_config.json"
alerts = []


# Ensure connected users file exists and is valid
if not os.path.exists(CONNECTED_USERS_FILE):
    with open(CONNECTED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# Ensure camera config exists with demo camera if not
if not os.path.exists(CAMERA_CONFIG):
    demo_config = {
        "cameras": [
            {
                "name": "Demo Camera",
                "url": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
            }
        ]
    }
    with open(CAMERA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(demo_config, f, indent=4)        
        
# === HEADER ===
def render_header():
    console.print("""
[bold blue]
    ___              _         _____                 __
   /   | ___  ____ _(_)____   / ___/____  ___  _____/ /__________ _
  / /| |/ _ \/ __ `/ / ___/   \__ \/ __ \/ _ \/ ___/ __/ ___/ __ `/
 / ___ /  __/ /_/ / (__  )   ___/ / /_/ /  __/ /__/ /_/ /  / /_/ /
/_/  |_\___/\__, /_/____/   /____/ .___/\___/\___/\__/\_/   \__,_/
           /____/               /_/[/bold blue]
    """)

# === NETWORK MONITOR ===
def monitor_network():
    console.print("[bold yellow]Live Network Traffic Monitor (10 packets)[/bold yellow]")
    try:
        interface = Prompt.ask("Enter interface to monitor", default="Ethernet" if os.name == 'nt' else "eth0")
        capture = pyshark.LiveCapture(interface=interface)
        capture.sniff(packet_count=10)
        table = Table(title="🌐 Captured Packets")
        table.add_column("Time")
        table.add_column("Source")
        table.add_column("Destination")
        table.add_column("Protocol")
        for pkt in capture:
            if hasattr(pkt, 'ip'):
                protocol = pkt.highest_layer
                source = pkt.ip.src
                dest = pkt.ip.dst
                timestamp = pkt.sniff_time.strftime("%H:%M:%S")
                table.add_row(timestamp, source, dest, protocol)
        console.print(table)
    except Exception as e:
        console.print(f"[red]Network capture failed:[/] {e}")
    console.input("Press Enter to continue...")

# === CAMERAS UI IMPLEMENTATION ===
def camera_ui_panel():
    with open(CAMERA_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)

    cameras = config.get("cameras", [])
    if not cameras:
        console.print("[red]No cameras configured.[/red]")
        return

    cam = cameras[0]
    root = tk.Tk()
    root.title(f"Camera Dashboard - {cam['name']}")
    root.geometry("800x600")

    sidebar = tk.Frame(root, width=200, bg="#2b2b2b")
    sidebar.pack(fill="y", side="left")
    tk.Label(sidebar, text="Camera Control Panel", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
    tk.Button(sidebar, text="Connect to Camera", command=lambda: webbrowser.open(cam["url"])).pack(pady=10)
    tk.Button(sidebar, text="Motion Detection Settings").pack(pady=10)

    header = tk.Frame(root, height=50, bg="#1e1e1e")
    header.pack(fill="x")
    tk.Label(header, text=cam["name"], bg="#1e1e1e", fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=20)
    tk.Button(header, text="Start Recording").pack(side="right", padx=10)
    tk.Button(header, text="Stop Recording").pack(side="right")

    root.mainloop()

def camera_control_menu():
    camera_ui_panel()

# === CONNECTED USERS LOG ===
def log_connected_user(username):
    users = []
    if os.path.exists(CONNECTED_USERS_FILE):
        try:
            with open(CONNECTED_USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = []
    users.append({"user": username, "time": datetime.now().isoformat()})
    with open(CONNECTED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users[-10:], f, indent=4)

def view_connected_users():
    if not os.path.exists(CONNECTED_USERS_FILE):
        console.print("[dim]No connected user history found.[/dim]")
        return
    with open(CONNECTED_USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    table = Table(title="🧑‍💻 Recent Logins")
    table.add_column("Username")
    table.add_column("Time")
    for u in users:
        table.add_row(u['user'], u['time'])
    console.print(table)


def view_connected_users():
    if not os.path.exists(CONNECTED_USERS_FILE):
        console.print("[dim]No connected user history found.[/dim]")
        return
    with open(CONNECTED_USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    table = Table(title="🧑‍💻 Recent Logins")
    table.add_column("Username")
    table.add_column("Time")
    for u in users:
        table.add_row(u['user'], u['time'])
    console.print(table)


# === PREFERENCES ===
def save_preferences(prefs):
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4)

def load_preferences():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def update_preferences():
    prefs = load_preferences()
    console.print("[cyan]Update Preferences:[/cyan]")
    timeout = Prompt.ask("Idle Timeout (minutes)", default=str(prefs.get("idle_timeout", 10)))
    notify = Prompt.ask("Enable Notifications (yes/no)", choices=["yes", "no"], default=prefs.get("notifications", "yes"))
    prefs.update({"idle_timeout": int(timeout), "notifications": notify})
    save_preferences(prefs)
    console.print("[green]✔ Preferences updated.[/green]")

# === LICENSE ===
def view_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            license_info = json.load(f)
        console.print("[bold cyan]License Info:[/bold cyan]")
        for k, v in license_info.items():
            console.print(f"{k}: {v}")
    else:
        console.print("[yellow]No license file found.[/yellow]")

def renew_license():
    console.print("[bold green]Redirecting to license renewal page...[/bold green]")
    webbrowser.open("https://aegis-secure.com/renew")

# === NOTIFICATIONS ===
def view_notifications():
    if not os.path.exists(NOTIFICATIONS_FILE):
        console.print("[dim]No notifications found.[/dim]")
        return
    with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
        notifs = json.load(f)
    table = Table(title="📢 Notifications")
    table.add_column("Time")
    table.add_column("Type")
    table.add_column("Message")
    for n in notifs:
        table.add_row(n["time"], n["type"], n["content"])
    console.print(table)

# === FEEDBACK ===
def write_feedback(feedback):
    feedbacks = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            feedbacks = json.load(f)
    feedbacks.append({"timestamp": datetime.now().isoformat(), "feedback": feedback})
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=4)

# === SCHEDULER ===
def save_schedule(data):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"enabled": "no"}

def run_scheduled_scans(username, role):
    def loop():
        while True:
            schedule = load_schedule()
            if schedule.get("enabled") == "yes":
                hour = int(schedule.get("hour", 3))
                now = datetime.now()
                if now.hour == hour and now.minute == 0:
                    if schedule["type"] == "quick":
                        quick_scan(username, role)
                    elif schedule["type"] == "full":
                        full_scan(username, role, "/")
                    elif schedule["type"] == "hybrid":
                        hybrid_scan(username, role)
                    time.sleep(60)
            time.sleep(30)
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

def schedule_scan():
    console.print("[cyan]Schedule Scan:[/cyan]")
    hour = Prompt.ask("Hour to run scan (0-23)", default="3")
    scan_type = Prompt.ask("Scan type", choices=["quick", "full", "hybrid"], default="quick")
    enabled = Prompt.ask("Enable schedule? (yes/no)", choices=["yes", "no"], default="yes")
    save_schedule({"hour": int(hour), "type": scan_type, "enabled": enabled})
    console.print(f"[green]✔ Scan scheduled daily at {hour}:00 as {scan_type}[/green]")

# === REPORTS ===
def open_last_report():
    if not os.path.exists(REPORTS_DIR):
        console.print("[dim]No reports found.[/dim]")
        return
    reports = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith((".pdf", ".html"))],
                     key=lambda x: os.path.getmtime(os.path.join(REPORTS_DIR, x)), reverse=True)
    if not reports:
        console.print("[dim]No reports available to open.[/dim]")
        return

    console.print("[bold cyan]Available Reports:[/bold cyan]")
    for idx, report in enumerate(reports):
        console.print(f"[{idx}] {report}")

    selected_idx = Prompt.ask("Select report index", default="0")
    try:
        selected_file = os.path.abspath(os.path.join(REPORTS_DIR, reports[int(selected_idx)]))
        webbrowser.open(f"file://{selected_file}")
        console.print(f"[green]✔ Opened report: {reports[int(selected_idx)]}[/green]")
    except (IndexError, ValueError):
        console.print("[red]Invalid selection.[/red]")

# === LOGIC ===
def export_scan_logs():
    if os.path.exists(LOG_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = f"exported_scan_log_{timestamp}.txt"
        shutil.copy(LOG_FILE, dest)
        console.print(f"[green]✔ Scan logs exported to {dest}[/green]")
    else:
        console.print("[red]No scan logs to export.[/red]")

def check_threats():
    if os.path.exists(THREATS_FILE):
        console.print("[bold red]Threats Found:[/bold red]")
        with open(THREATS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                console.print(f"[red]- {line.strip()}[/red]")
    else:
        console.print("[green]No threats logged.[/green]")

def show_alerts():
    if not alerts:
        console.print("[green]No alerts at this time.[/green]")
    else:
        table = Table(title="🔔 Live Alerts")
        table.add_column("Time")
        table.add_column("Message")
        for alert in alerts:
            table.add_row(alert[0], alert[1])
        console.print(table)

# === AI RECOMMENDATION ===
def suggest_scan_type():
    suggestion = random.choice(["quick", "full", "hybrid"])
    console.print(f"[dim]🤖 AI suggests a '{suggestion}' scan based on recent patterns.[/dim]")

# === SCANS ===
def scan_menu(username, role):
    while True:
        console.clear()
        render_header()
        suggest_scan_type()
        console.print("[bold]Scan Menu[/bold]")
        console.print("[1] Quick Scan")
        console.print("[2] Full Scan")
        console.print("[3] Hybrid Scan")
        console.print("[4] Export Scan Logs")
        console.print("[5] Check Threats")
        console.print("[6] Network Traffic Monitor")
        console.print("[7] License Info")
        console.print("[8] Notifications")
        console.print("[9] Submit Feedback")
        console.print("[0] Back")

        choice = Prompt.ask("Select", choices=[str(i) for i in range(10)])

        if choice == "1":
            quick_scan(username, role)
        elif choice == "2":
            full_scan(username, role, "/")
        elif choice == "3":
            hybrid_scan(username, role)
        elif choice == "4":
            export_scan_logs()
        elif choice == "5":
            check_threats()
        elif choice == "6":
            monitor_network()
        elif choice == "7":
            view_license()
        elif choice == "8":
            view_notifications()
        elif choice == "9":
            fb = Prompt.ask("Leave feedback or rate 1-5")
            write_feedback(fb)
            console.print("[green]✔ Feedback recorded.[/green]")
        elif choice == "0":
            break
        console.input("Press Enter to return to Scan Menu...")

# === DASHBOARD ===
def client_dashboard(username, role):
    log_connected_user(username)
    run_scheduled_scans(username, role)
    while True:
        console.clear()
        render_header()
        console.print(f"[bold green]Logged in as: {username} ({role})[/bold green]\n")

        console.print("[1] 🔍 Scans")
        console.print("[2] 📄 View Last Report")
        console.print("[3] ⚙️ Update Preferences")
        console.print("[4] ⏰ Schedule Scan")
        console.print("[5] 📢 View Notifications")
        console.print("[6] 📜 License Info")
        console.print("[7] 🔔 Show Live Alerts")
        console.print("[8] 📝 Submit Feedback")
        console.print("[9] 🧑‍💻 View Connected Users")
        console.print("[10] 📷 Camera Control")
        console.print("[0] ❌ Exit")

        choice = Prompt.ask("Select option", choices=[str(i) for i in range(11)])

        if choice == "1":
            scan_menu(username, role)
        elif choice == "2":
            open_last_report()
        elif choice == "3":
            update_preferences()
        elif choice == "4":
            schedule_scan()
        elif choice == "5":
            view_notifications()
        elif choice == "6":
            view_license()
        elif choice == "7":
            show_alerts()
        elif choice == "8":
            fb = Prompt.ask("Leave feedback or rate 1-5")
            write_feedback(fb)
            console.print("[green]✔ Feedback recorded.[/green]")
        elif choice == "9":
            view_connected_users()
        elif choice == "10":
             camera_ui_panel()
        elif choice == "0":
            break
        console.input("\n[white]Press Enter to return to dashboard...[/white]")