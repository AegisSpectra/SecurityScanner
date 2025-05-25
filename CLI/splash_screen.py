"""
Splash Screen Module

This module provides the initial boot animation and splash screen for the
Aegis Spectra CLI application. It creates a Matrix-style animation effect
followed by the application banner.
"""

# Standard library imports
import os
import random
import time

# Third-party imports
from rich.console import Console
from pyfiglet import Figlet

# Constants
ANIMATION_CHARS = "01█▓▒░"
ANIMATION_LINES = 20
ANIMATION_DELAY = 0.05
BOOT_DELAY = 1.0

# Initialize console
console = Console()

def splash_screen():
    """
    Display the application splash screen with a Matrix-style animation.
    
    The function performs the following:
    1. Shows a boot message
    2. Displays a Matrix-style animation
    3. Shows the application banner
    4. Indicates system readiness
    """
    width = os.get_terminal_size().columns
    fig = Figlet(font="slant")
    banner = fig.renderText("Aegis Spectra")

    # Clear screen and show boot message
    console.clear()
    console.print("[bold green]Booting Aegis Spectra CLI System...[/bold green]")
    time.sleep(BOOT_DELAY)

    # Matrix animation
    for _ in range(ANIMATION_LINES):
        line = "".join(random.choice(ANIMATION_CHARS) for _ in range(width))
        console.print(f"[green]{line}[/green]", end="")
        time.sleep(ANIMATION_DELAY)

    # Show banner and ready message
    console.clear()
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[bold green]System Ready.[/bold green]\n")
    time.sleep(BOOT_DELAY)