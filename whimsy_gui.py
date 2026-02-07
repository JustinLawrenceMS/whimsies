#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys
import threading
import random

# Path to local resources
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
WHIMSY_SCRIPT = os.path.join(PROJECT_DIR, "whimsy.py")
INSTALLER_SCRIPT = os.path.join(PROJECT_DIR, "install_whimsy.sh")
PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/com.whimsy.daily.plist")

def get_python_bin():
    # Try to find .venv python, else system python
    venv_python = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
    if os.path.exists(venv_python) and os.access(venv_python, os.X_OK):
        return venv_python
    return sys.executable

PYTHON_BIN = get_python_bin()

class WhimsyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💎💖 Whimsy Love Notes 💖💎")
        self.root.geometry("450x450")
        self.root.resizable(False, False)
        
        # Soft pink background
        bg_color = '#FFF0F5'
        self.root.configure(bg=bg_color)

        try:
            # Try to set app icon if it exists (skip for now to avoid errors)
            pass 
        except Exception:
            pass

        # Create Wallpaper Canvas
        self.canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Draw random hearts
        hearts = ["💖", "💘", "💝", "💓", "💕", "💟", "❣️", "❤️", "✨", "💎", "💍", "💫", "👑"]
        for _ in range(1000):
            x = random.randint(0, 450)
            y = random.randint(0, 450)
            heart = random.choice(hearts)
            size = random.randint(10, 30)
            color = random.choice(["#FFB6C1", "#FF69B4", "#FF1493", "#DB7093"]) # Varying pinks
            self.canvas.create_text(x, y, text=heart, font=('Arial', size), fill=color)

        # Styles
        style = ttk.Style()
        style.configure("TButton", padding=8, font=('Helvetica', 13))

        # Header
        header = tk.Label(root, text="✨👑💖 Whimsy for My Queen 💖👑✨", font=('Helvetica', 22, 'bold'), 
                          bg=bg_color, fg='#D81B60')
        header.pack(pady=30)
        
        # Status Frame
        self.status_frame = tk.Frame(root, bg=bg_color)
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Checking status... 💓💝💎", 
                                     font=('Helvetica', 12), bg=bg_color, fg="#555")
        self.status_label.pack()

        # Actions Frame
        self.actions_frame = tk.Frame(root, bg=bg_color)
        self.actions_frame.pack(pady=20, fill=tk.X)

        self.btn_send = ttk.Button(self.actions_frame, text="💌 Send Love Note Now 💘🚀💎", command=self.send_now)
        self.btn_send.pack(fill=tk.X, pady=8, padx=50)

        self.btn_install = ttk.Button(self.actions_frame, text="✅ Enable Daily Love (08:00) ⏰💕💍", command=self.install_schedule)
        self.btn_install.pack(fill=tk.X, pady=8, padx=50)

        self.btn_uninstall = ttk.Button(self.actions_frame, text="🛑 Stop Daily Love 💔🥀🌧️", command=self.uninstall_schedule)
        self.btn_uninstall.pack(fill=tk.X, pady=8, padx=50)

        # Footer
        footer = tk.Label(root, text="Made with endless love and ❤️❤️❤️💎✨", font=('Helvetica', 11, 'italic'), 
                          bg=bg_color, fg="#888")
        footer.pack(side=tk.BOTTOM, pady=25)

        self.refresh_status()

    def refresh_status(self):
        if os.path.exists(PLIST_PATH):
            self.status_label.config(text="✨💎 Status: Daily Love Active! 💖🥰🎉", fg="#2E7D32")
            self.btn_install.state(['disabled'])
            self.btn_uninstall.state(['!disabled'])
        else:
            self.status_label.config(text="💤🖤 Status: Daily Love Paused 🥀💔🌧️", fg="#C62828")
            self.btn_install.state(['!disabled'])
            self.btn_uninstall.state(['disabled'])

    def run_command(self, cmd, success_msg):
        def task():
            try:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.root.after(0, lambda: messagebox.showinfo("Success ✨💎💖", success_msg))
                self.root.after(0, self.refresh_status)
            except subprocess.CalledProcessError as e:
                err_msg = f"Command failed with code {e.returncode}"
                self.root.after(0, lambda: messagebox.showerror("Error 😢🌧️", err_msg))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error 😢🌧️", str(e)))

        threading.Thread(target=task).start()

    def send_now(self):
        if messagebox.askyesno("Confirm 💌💕💎", "Send a love note immediately? 🏹💘✨"):
            cmd = [PYTHON_BIN, WHIMSY_SCRIPT, "--send-now"]
            self.run_command(cmd, "Email sent successfully! 🚀💌💞💎")

    def install_schedule(self):
        # Default to 08:00
        cmd = [INSTALLER_SCRIPT, "--launchd", "--install", "--python", PYTHON_BIN, "--time", "08:00", "--project-dir", PROJECT_DIR]
        self.run_command(cmd, "Daily schedule installed for 08:00! 🗓️💖💍✨")

    def uninstall_schedule(self):
        if messagebox.askyesno("Confirm 💔🥺🍂", "Stop the daily emails? 😢💔🌧️"):
            # Unload simple via launchctl
            cmd = ["launchctl", "unload", PLIST_PATH]
            # Also remove the file
            def task():
                try:
                    subprocess.call(cmd) # Ignore error if not loaded
                    if os.path.exists(PLIST_PATH):
                        os.remove(PLIST_PATH)
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Schedule uninstalled. 😴🥀🖤"))
                    self.root.after(0, self.refresh_status)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
            threading.Thread(target=task).start()

if __name__ == "__main__":
    if not os.path.exists(WHIMSY_SCRIPT):
        messagebox.showerror("Error", f"Missing whimsy.py at {WHIMSY_SCRIPT}")
        sys.exit(1)
        
    root = tk.Tk()
    app = WhimsyApp(root)
    root.mainloop()
