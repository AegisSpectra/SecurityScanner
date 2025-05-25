# threat_engine.py
import json
from datetime import datetime
from rich.console import Console
import ctypes
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# === FILE PATHS ===
ALERTS_FILE = "alerts.json"
AUDIT_LOG = "system_audit.log"
RESPONSE_LOG = "response_log.txt"
DLL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "core", "aegis_core.dll"))

console = Console()

# === DLL LOADING + INTEGRITY CHECK ===
def check_dll_integrity(path):
    if not os.path.exists(path):
        raise FileNotFoundError("DLL not found.")
    if os.path.getsize(path) < 1000:
        raise ValueError("DLL appears incomplete or corrupted.")

try:
    check_dll_integrity(DLL_PATH)
    aegis = ctypes.CDLL(DLL_PATH)
    aegis.calculate_threat_score.argtypes = [ctypes.c_char_p]
    aegis.calculate_threat_score.restype = ctypes.c_int
except Exception as e:
    console.print(f"[red]Failed to load threat engine DLL:[/] {e}")
    raise SystemExit(1)

# === LOGGING FUNCTIONS ===
def audit_log(entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {entry}\n")

def log_alert(alert_type, message, score):
    alert = {
        "time": datetime.now().isoformat(),
        "type": alert_type,
        "message": message,
        "risk_score": score
    }
    try:
        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(alert)
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data[-100:], f, indent=4)

    with open(RESPONSE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{alert['time']}] ACTION: {alert_type} | MSG: {message} | SCORE: {score}\n")

    if alert_type in ("DELETE", "QUARANTINE"):
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Aegis Alert", f"⚠ Action: {alert_type} for threat: {message}")
            root.destroy()
        except:
            pass

# === SMART RESPONSE ENGINE ===
def smart_response(action, description):
    if action == "DELETE":
        subprocess.run("taskkill /f /im suspicious.exe", shell=True)
        audit_log(f"Triggered kill for suspicious process due to: {description}")
    elif action == "QUARANTINE":
        subprocess.run("netsh advfirewall set allprofiles state off", shell=True)
        audit_log(f"Triggered firewall lockdown due to: {description}")
    elif action == "ALERT":
        audit_log(f"Alert triggered, notifying analyst: {description}")

# === THREAT EVALUATION ENGINE ===
def evaluate_threat(description: str, severity_score: int = None) -> str:
    if severity_score is None:
        try:
            severity_score = aegis.calculate_threat_score(description.encode())
        except Exception as e:
            console.print(f"[red]Error calculating threat score:[/] {e}")
            severity_score = 0

    audit_log(f"Evaluating threat: {description} | Score: {severity_score}")

    if severity_score < 30:
        action = "IGNORE"
    elif severity_score < 60:
        action = "ALERT"
    elif severity_score < 85:
        action = "QUARANTINE"
    else:
        action = "DELETE"

    log_alert(action, description, severity_score)
    smart_response(action, description)
    console.print(f"[bold magenta]Threat Decision:[/] {action} ({severity_score})")
    return action

# === AI REPORT GENERATOR ===
def generate_ai_report(scan_type: str, username: str, role: str, scanned: int, detected: int, descriptions: list):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = {
        "type": scan_type,
        "user": username,
        "role": role,
        "scanned": scanned,
        "detected": detected,
        "time": timestamp,
        "descriptions": descriptions
    }
    path = f"SOC_AI_report_{scan_type}_{username}_{timestamp.replace(':', '-').replace(' ', '_')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    console.print(f"[green]✔ AI Report saved to {path}[/green]")

# === TEST ENTRY POINT ===
if __name__ == "__main__":
    evaluate_threat("Suspicious behavior in process explorer.exe")
