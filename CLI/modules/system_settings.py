import json
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

SETTINGS_FILE = "settings.json"
console = Console()

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "auto_defense": True,
            "debug_mode": False,
            "default_scan_dir": "/",
            "virustotal_api_key": "",
        }
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def display_settings(settings):
    panel = Panel(
        f"Auto-Defense: {'ON' if settings['auto_defense'] else 'OFF'}\n"
        f"Debug Mode: {'ENABLED' if settings['debug_mode'] else 'DISABLED'}\n"
        f"Default Scan Directory: {settings['default_scan_dir']}\n"
        f"VirusTotal API Key: {'Set' if settings['virustotal_api_key'] else 'Not Set'}",
        title="Current System Settings",
        border_style="cyan"
    )
    console.print(panel)

def system_settings_menu():
    settings = load_settings()

    while True:
        console.clear()
        display_settings(settings)
        console.print("[bold blue]System Settings Menu[/bold blue]")
        console.print("[1] Toggle Auto-Defense on Startup")
        console.print("[2] Edit VirusTotal API Key")
        console.print("[3] Set Default Scan Directory")
        console.print("[4] Toggle Debug Mode")
        console.print("[5] View Settings")
        console.print("[6] Save & Exit")
        console.print("[0] Cancel")
        choice = Prompt.ask("Select option", choices=["1","2","3","4","5","6","0"])

        if choice == "1":
            settings["auto_defense"] = not settings["auto_defense"]
        elif choice == "2":
            new_key = Prompt.ask("Enter new VirusTotal API Key")
            settings["virustotal_api_key"] = new_key
        elif choice == "3":
            new_path = Prompt.ask("Enter new default scan directory")
            settings["default_scan_dir"] = new_path
        elif choice == "4":
            settings["debug_mode"] = not settings["debug_mode"]
        elif choice == "5":
            display_settings(settings)
            console.input("Press Enter to return...")
        elif choice == "6":
            save_settings(settings)
            console.print("[green]✔ Settings saved.[/green]")
            break
        elif choice == "0":
            break
