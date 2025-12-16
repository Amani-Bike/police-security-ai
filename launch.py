#!/usr/bin/env python3
"""
Cross-platform launcher for Police Security AI Platform
"""
import os
import sys
import subprocess
import platform
import time
import threading
import webbrowser


def run_command(cmd, desc=""):
    """Run a command and show progress"""
    print(f"{desc}...")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return False
    return True


def open_browser():
    """Open the browser after a delay to allow server to start"""
    time.sleep(3)  # Wait for server to start
    print("\nOpening browser at http://localhost:8000...")
    webbrowser.open("http://localhost:8000")


def main():
    print("="*50)
    print("SafetyNet - Police Security AI Platform")
    print("="*50)

    # Determine the system
    system = platform.system().lower()
    print(f"Running on: {system}")

    # Install dependencies
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                       "Installing dependencies"):
        print("Failed to install dependencies. Please run 'pip install -r requirements.txt' manually.")
        input("Press Enter to continue...")
        return

    # Initialize database
    if not run_command([sys.executable, "init_db.py"],
                       "Initializing database"):
        print("Database initialization failed. Continuing anyway...")

    # Start the browser opener in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Start the server
    print("\nStarting the server...")
    print("The browser will open automatically in a few seconds...")
    print("Press Ctrl+C to stop the server\n")

    uvicorn_cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    try:
        subprocess.run(uvicorn_cmd)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        print("Thank you for using SafetyNet!")


if __name__ == "__main__":
    main()