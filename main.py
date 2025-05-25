"""
Aegis Spectra CLI - Main Entry Point

This module serves as the main entry point for the Aegis Spectra CLI application.
It handles user authentication, role-based access control, and directs users to
their appropriate dashboards based on their roles.

The application supports multiple user roles including:
- Super Admin
- Private Client
- Business Client
- SOC Analyst
"""

# Standard library imports
import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath("."))

# Local application imports
from CLI.splash_screen import splash_screen
from CLI.login import login
from CLI.loading import loading_sequence
from CLI.roles.super_admin_menu import super_admin_cli
from CLI.roles.private_client_dashboard import client_dashboard
from CLI.roles.business_client_dashboard import client_business_dashboard
from CLI.roles.soc_dashboard import soc_dashboard_menu

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "DATABASE", "aegis_advanced_structured.db")

def main():
    """
    Main application entry point.
    
    Handles the application flow:
    1. Displays splash screen
    2. Authenticates user
    3. Shows loading sequence
    4. Directs to appropriate dashboard based on user role
    """
    splash_screen()
    username, role = login()
    
    if username and role:
        loading_sequence(username)
        role = role.lower()  # Normalize to lowercase for safety
        print(f"[DEBUG] Logged in as: {username} | Role: {role}")

        # Role-based dashboard routing
        if role == "super_admin" and username == "admin_ilya":
            super_admin_cli(username)
        elif role == "private_client":
            client_dashboard(username, role)
        elif role == "client_business":
            client_business_dashboard(username)
        elif role == "soc":
            soc_dashboard_menu(username)
        else:
            print("[!] No dashboard available for this role.")

if __name__ == "__main__":
    main()
