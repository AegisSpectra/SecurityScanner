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
import numpy as np
from SCANNER.scanner import quick_scan, full_scan, hybrid_scan
import pyshark
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
CAMERA_CONFIG = "CAMERA/config.json"
VIDEO_LOG_DIR = "video_log"
alerts = []

# Ensure camera config exists with demo camera if not
if not os.path.exists(CAMERA_CONFIG):
    config_dir = os.path.dirname(CAMERA_CONFIG)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    demo_config = {
        "cameras": [
            {
                "name": "Demo Camera",
                "url": "demo"  # Use fake video
            }
        ]
    }
    with open(CAMERA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(demo_config, f, indent=4)

if not os.path.exists(VIDEO_LOG_DIR):
    os.makedirs(VIDEO_LOG_DIR)

# === CAMERAS UI IMPLEMENTATION ===
def camera_ui_panel():
    with open(CAMERA_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)

    cameras = config.get("cameras", [])
    if not cameras:
        console.print("[red]No cameras configured.[/red]")
        return

    root = tk.Tk()
    root.title("Camera Dashboard - Multi View")
    root.geometry("1200x800")
    root.configure(bg="#1e1e1e")

    header = tk.Frame(root, height=50, bg="#121212")
    header.pack(fill="x")
    tk.Label(header, text="Multi-Camera Control Panel", bg="#121212", fg="white", font=("Arial", 16, "bold")).pack(side="left", padx=20)

    grid_frame = tk.Frame(root, bg="#2b2b2b")
    grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

    video_labels = []
    caps = []
    recording_flags = {}

    for i, cam in enumerate(cameras[:16]):
        if cam["url"] == "demo":
            cap = None  # No real camera
        else:
            cap = cv2.VideoCapture(cam["url"])
            if not cap.isOpened():
                cap = None  # fallback to dummy
                console.print(f"[yellow]No device connected for: {cam['name']}[/yellow]")

        caps.append(cap)
        label = tk.Label(grid_frame, text=cam["name"], bg="black")
        label.grid(row=i//4, column=i%4, padx=5, pady=5)
        video_labels.append((label, cap, cam["name"]))
        recording_flags[cam["name"]] = False

    def update_frames():
        for label, cap, name in video_labels:
            if cap:
                ret, frame = cap.read()
                if not ret:
                    frame = np.zeros((180, 280, 3), dtype=np.uint8)
                    cv2.putText(frame, "No signal", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                else:
                    frame = cv2.resize(frame, (280, 180))
            else:
                frame = 255 * np.ones((180, 280, 3), dtype=np.uint8)
                cv2.putText(frame, f"{name}\nNo Device", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)

        root.after(100, update_frames)

    control_bar = tk.Frame(root, height=40, bg="#121212")
    control_bar.pack(fill="x")
    tk.Button(control_bar, text="Start Recording").pack(side="right", padx=10)
    tk.Button(control_bar, text="Stop Recording").pack(side="right")

    update_frames()
    root.mainloop()

    for _, cap, _ in video_labels:
        if cap:
            cap.release()
    cv2.destroyAllWindows()

def camera_control_menu():
    camera_ui_panel()
