import time
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

DEBUG_LOG = "debug.log"
console = Console()

# פונקציה גלובלית שניתן לייבא בכל מודול

def log_debug(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    if os.getenv("AEGIS_DEBUG") == "1":
        console.print(f"[dim]{entry}[/dim]")

# סימולציה להצגת רצף Debug מדומה

def simulate_debug_sequence():
    steps = [
        "Initializing engine...",
        "Checking memory blocks...",
        "Analyzing process tree...",
        "Verifying network integrity...",
        "AI module feedback loop...",
        "Finalizing handshake with kernel..."
    ]
    for step in steps:
        log_debug(step)
        time.sleep(0.5)

# צפייה בקובץ debug.log (20 שורות אחרונות)

def view_debug_log():
    if not os.path.exists(DEBUG_LOG):
        console.print("[dim]No debug log found.[/dim]")
        return
    with open(DEBUG_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()[-20:]
    table = Table(title="🛠️ Debug Log Tail")
    table.add_column("Recent Debug Entries", style="dim")
    for line in lines:
        table.add_row(line.strip())
    console.print(table)

# תפריט Debug Tools

def debug_tools_menu():
    while True:
        console.clear()
        console.print("[bold blue]Developer / Debug Tools[/bold blue]")
        console.print("[1] Simulate Debug Sequence")
        console.print("[2] View Debug Log")
        console.print("[3] Clear Debug Log")
        console.print("[0] Back")
        choice = Prompt.ask("Select", choices=["1","2","3","0"])

        if choice == "1":
            simulate_debug_sequence()
            console.input("Done. Press Enter...")
        elif choice == "2":
            view_debug_log()
            console.input("Press Enter to return...")
        elif choice == "3":
            open(DEBUG_LOG, "w").close()
            console.print("[green]✔ Debug log cleared[/green]")
            time.sleep(1)
        elif choice == "0":
            break

# לשילוב בתפריט super_admin_menu:
# from CLI.modules.debug_tools import debug_tools_menu
# ואז בתוך elif:
# elif choice == "8":
#     debug_tools_menu()
