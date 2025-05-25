from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pyfiglet import Figlet
import time
import psutil
import socket
import os

console = Console()

def show_banner():
    fig = Figlet(font='slant')  # נסה גם: 'block', 'cybermedium', 'ansi_shadow'
    banner = fig.renderText("Aegis Spectra")
    console.print(f"[bold cyan]{banner}[/bold cyan]")

def check_network():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

def check_cpu():
    return psutil.cpu_percent(interval=1)

def check_memory():
    return psutil.virtual_memory().percent

def check_home_dir():
    return os.path.exists(os.path.expanduser("~"))

def loading_sequence(username):
    console.clear()
    show_banner()
    console.rule(f"[bold green]Initializing session for [cyan]{username}[/cyan]...")

    checks = [
        ("Checking network", check_network),
        ("Checking CPU load", check_cpu),
        ("Checking memory usage", check_memory),
        ("Verifying user directory", check_home_dir),
    ]

    with Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:

        for label, func in checks:
            task = progress.add_task(label, total=None)
            time.sleep(1)
            result = func()
            progress.update(task, description=f"{label}... ✔" if result else f"{label}... ✖")
            progress.remove_task(task)

    console.print("\n[bold green]✔ Login successful! Welcome to Aegis Spectra CLI[/bold green]\n")
    time.sleep(1)
