#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys
import threading

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
        self.root.title("Whimsy Control Panel")
        self.root.geometry("400x320")
        self.root.resizable(False, False)

        try:
            # Try to set app icon if it exists (skip for now to avoid errors)
            pass 
        except Exception:
            pass

        # Styles
        style = ttk.Style()
        style.configure("TButton", padding=6, font=('Helvetica', 12))
        style.configure("TLabel", font=('Helvetica', 11))
        style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))

        # Header
        header = ttk.Label(root, text="❤️ Whimsy for My Queen", style="Header.TLabel")
        header.pack(pady=20)

        # Status Frame
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = ttk.Label(self.status_frame, text="Checking status...", foreground="gray")
        self.status_label.pack()

        # Actions Frame
        self.actions_frame = ttk.Frame(root)
        self.actions_frame.pack(pady=20)

        self.btn_send = ttk.Button(self.actions_frame, text="💌 Send One Email Now", command=self.send_now)
        self.btn_send.pack(fill=tk.X, pady=5)

        self.btn_install = ttk.Button(self.actions_frame, text="✅ Install Daily Schedule (08:00)", command=self.install_schedule)
        self.btn_install.pack(fill=tk.X, pady=5)

        self.btn_uninstall = ttk.Button(self.actions_frame, text="🛑 Stop/Uninstall Schedule", command=self.uninstall_schedule)
        self.btn_uninstall.pack(fill=tk.X, pady=5)

        # Footer
        footer = ttk.Label(root, text="Made with love", font=('Helvetica', 10), foreground="#aaa")
        footer.pack(side=tk.BOTTOM, pady=10)

        self.refresh_status()

    def refresh_status(self):
        if os.path.exists(PLIST_PATH):
            self.status_label.config(text="Status: Daily Schedule INSTALLED ✅", foreground="green")
            self.btn_install.state(['disabled'])
            self.btn_uninstall.state(['!disabled'])
        else:
            self.status_label.config(text="Status: Daily Schedule NOT INSTALLED", foreground="#B00020")
            self.btn_install.state(['!disabled'])
            self.btn_uninstall.state(['disabled'])

    def run_command(self, cmd, success_msg):
        def task():
            try:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
                self.root.after(0, self.refresh_status)
            except subprocess.CalledProcessError as e:
                err_msg = f"Command failed with code {e.returncode}"
                self.root.after(0, lambda: messagebox.showerror("Error", err_msg))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=task).start()

    def send_now(self):
        if messagebox.askyesno("Confirm", "Send a love note immediately?"):
            cmd = [PYTHON_BIN, WHIMSY_SCRIPT, "--send-now"]
            self.run_command(cmd, "Email sent successfully!")

    def install_schedule(self):
        # Default to 08:00
        cmd = [INSTALLER_SCRIPT, "--launchd", "--install", "--python", PYTHON_BIN, "--time", "08:00", "--project-dir", PROJECT_DIR]
        self.run_command(cmd, "Daily schedule installed for 08:00!")

    def uninstall_schedule(self):
        if messagebox.askyesno("Confirm", "Stop the daily emails?"):
            # Unload simple via launchctl
            cmd = ["launchctl", "unload", PLIST_PATH]
            # Also remove the file
            def task():
                try:
                    subprocess.call(cmd) # Ignore error if not loaded
                    if os.path.exists(PLIST_PATH):
                        os.remove(PLIST_PATH)
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Schedule uninstalled."))
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
