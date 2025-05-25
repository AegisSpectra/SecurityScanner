import psutil
import shutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()

def system_overview():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    net = psutil.net_io_counters()

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")

    table.add_row("🧠 CPU Usage", f"{cpu}%")
    table.add_row("💾 RAM Usage", f"{mem.percent}% ({round(mem.used / (1024 ** 3), 2)} GB / {round(mem.total / (1024 ** 3), 2)} GB)")
    table.add_row("🗄️ Disk Usage", f"{round(disk.used / (1024 ** 3), 2)} GB / {round(disk.total / (1024 ** 3), 2)} GB")
    table.add_row("🌐 Network Sent", f"{round(net.bytes_sent / (1024 ** 2), 2)} MB")
    table.add_row("🌐 Network Received", f"{round(net.bytes_recv / (1024 ** 2), 2)} MB")
    table.add_row("🕒 Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    console.print(Panel(table, title="🖥️ System Overview", subtitle="Live Stats", style="bold green"))
    console.input("\nPress Enter to return...")