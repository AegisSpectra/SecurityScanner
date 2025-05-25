# === SCANNER MODULE WITH AI THREAT ENGINE ===
import os
import psutil
import sqlite3
import random
import time
import hashlib
import yara
import requests
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt
from ENGINE.threat_engine import evaluate_threat, generate_ai_report

DB_PATH = "DATABASE/aegis_advanced_structured.db"
LOG_FILE = "scan_log.txt"
AUDIT_LOG = "system_audit.log"
RESPONSE_LOG = "response_log.txt"
QUARANTINE_DIR = "QUARANTINED"
console = Console()
VIRUSTOTAL_API_KEY = "2b75975da66d30c3e0d405ac7c487a6bc6263a3786bcf09f56ae0a30c27a9a66"

os.makedirs(QUARANTINE_DIR, exist_ok=True)

def audit_log(entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {entry}\n")

def log_response(action, filepath, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESPONSE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Action: {action} | File: {filepath} | Status: {status}\n")

def auto_quarantine(filepath):
    try:
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = os.path.join(QUARANTINE_DIR, timestamp)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, filename)
        with open(filepath, "rb") as src, open(target_path, "wb") as dst:
            dst.write(src.read())
        file_hash = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
        audit_log(f"Auto-Quarantine: {filename} | Hash: {file_hash} | Location: {target_path}")
        log_response("QUARANTINE", filepath, "success")
        console.print(f"[yellow]File quarantined:[/] {target_path}")
    except Exception as e:
        log_response("QUARANTINE", filepath, f"failed: {e}")
        console.print(f"[red]Quarantine failed:[/] {e}")

def threat_response(filepath):
    action = evaluate_threat(f"Detected threat in file: {filepath}")
    if action == "IGNORE":
        audit_log(f"Ignored threat: {filepath}")
        log_response("IGNORE", filepath, "ignored")
    elif action == "QUARANTINE":
        auto_quarantine(filepath)
    elif action == "DELETE":
        try:
            os.remove(filepath)
            audit_log(f"Deleted threat: {filepath}")
            log_response("DELETE", filepath, "success")
            console.print(f"[red]Deleted:[/] {filepath}")
        except Exception as e:
            log_response("DELETE", filepath, f"failed: {e}")
            console.print(f"[red]Delete failed:[/] {e}")

def match_yara_rules(filepath):
    try:
        if not os.path.exists('rules.yar'):
            console.print("[dim]YARA rules file not found: rules.yar[/dim]")
            return []
        rules = yara.compile(filepath='rules.yar')
        matches = rules.match(filepath)
        return matches
    except Exception as e:
        console.print(f"[dim]YARA error:[/] {e}")
        return []

def scan_file_with_virustotal(filepath):
    try:
        with open(filepath, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and 'data' in response.json():
            result = response.json()['data']['attributes']
            if result['last_analysis_stats']['malicious'] > 0:
                return True
    except Exception as e:
        console.print(f"[red]VirusTotal error:[/] {e}")
    return False

def quick_scan(username, role):
    console.clear()
    console.print("[bold green]>>> Starting Quick Scan[/bold green]")
    scanned_count = 0
    detected = 0
    descriptions = []
    with Progress(SpinnerColumn(), "[progress.description]{task.description}", TimeElapsedColumn(), transient=True) as progress:
        task = progress.add_task("[yellow]Scanning processes...", total=None)
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                scanned_count += 1
                if proc.info['cpu_percent'] > 70 or proc.info['memory_percent'] > 50:
                    description = f"High CPU/Memory process: {proc.info['name']}"
                    evaluate_threat(description)
                    descriptions.append(description)
                    detected += 1
            except:
                continue
    console.print(f"[green]✔ Quick Scan Completed. Scanned {scanned_count} processes. Suspicious: {detected}[/]")
    generate_ai_report("Quick", username, role, scanned_count, detected, descriptions)

def full_scan(username, role, directory="/"):
    console.clear()
    console.print("[bold green]>>> Starting Full Scan[/bold green]")
    suspicious_ext = ['.exe', '.dll', '.bat', '.scr', '.vbs', '.ps1', '.js']
    scanned_files = 0
    detected_files = 0
    descriptions = []
    with Progress("[progress.description]{task.description}", BarColumn(), TimeElapsedColumn()) as progress:
        task = progress.add_task("[yellow]Analyzing files...", total=None)
        for dirpath, _, filenames in os.walk(directory):
            for file in filenames:
                scanned_files += 1
                filepath = os.path.join(dirpath, file)
                if os.path.splitext(file)[1].lower() in suspicious_ext:
                    yara_hits = match_yara_rules(filepath)
                    vt_flagged = scan_file_with_virustotal(filepath)
                    if yara_hits or vt_flagged:
                        description = f"Suspicious file: {filepath}"
                        evaluate_threat(description)
                        threat_response(filepath)
                        descriptions.append(description)
                        detected_files += 1
    console.print(f"[green]✔ Full Scan Completed. Files scanned: {scanned_files}. Threats detected: {detected_files}[/]")
    generate_ai_report("Full", username, role, scanned_files, detected_files, descriptions)

def hybrid_scan(username, role):
    console.clear()
    console.print("[bold blue]>>> Starting Hybrid Scan[/bold blue]")
    quick_scan(username, role)
    full_scan(username, role, directory="/")
    console.print("[cyan]✔ Hybrid Scan Complete.[/]")
