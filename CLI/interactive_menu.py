from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from SCANNER.scanner import quick_scan, full_scan, hybrid_scan
from CORE.export_pdf import export_log_to_pdf
from CORE.view_reports import view_reports

style = Style.from_dict({
    '': '#00ffcc',
    'completion-menu.completion': 'bg:#008800 #ffffff',
    'completion-menu.completion.current': 'bg:#00ffcc #000000',
})

menu_completer = WordCompleter([
    'quick', 'full', 'hybrid', 'export', 'view', 'exit'
], ignore_case=True)

def interactive_cli(username, role):
    print(f"\nWelcome {username} ({role}) - Type a command or press TAB for options.\n")
    while True:
        try:
            command = prompt("Select command > ", completer=menu_completer, style=style).strip().lower()
            if command == "quick":
                quick_scan(username, role)
            elif command == "full":
                directory = input("Enter directory to scan (default: /): ").strip() or "/"
                full_scan(username, role, directory)
            elif command == "hybrid":
                hybrid_scan(username, role)
            elif command == "export":
                export_log_to_pdf()
            elif command == "view":
                view_reports()
            elif command == "exit":
                print("Exiting interactive menu. Goodbye!")
                break
            else:
                print("Unknown command. Try again.")
        except KeyboardInterrupt:
            print("\nExiting on user interrupt.")
            break