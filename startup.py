import os
import sys
import subprocess
import argparse
import webbrowser
import time
import threading


def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def initialize_database():
    """Initialize the database by running init_db.py"""
    print("Initializing database...")
    try:
        subprocess.check_call([sys.executable, "init_db.py"])
        print("Database initialized successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing database: {e}")
        return False


def run_server():
    """Run the FastAPI server"""
    print("Starting the server...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "uvicorn", "backend.app:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
        return False


def open_browser():
    """Open the browser after a delay to allow server to start"""
    time.sleep(3)  # Wait for server to start
    print("\nOpening browser at http://localhost:8000...")
    webbrowser.open("http://localhost:8000")


def setup_and_run():
    """Complete setup: install dependencies, initialize database, and run server"""
    if not install_dependencies():
        print("Failed to install dependencies. Exiting.")
        return False

    if not initialize_database():
        print("Failed to initialize database. Continuing anyway...")

    print("\nAll setup complete! Starting the server...")

    # Start the browser opener in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Run the server
    run_server()


def main():
    parser = argparse.ArgumentParser(description="Police Security AI Startup Script")
    parser.add_argument("--install", action="store_true", help="Install dependencies only")
    parser.add_argument("--init-db", action="store_true", help="Initialize database only")
    parser.add_argument("--run", action="store_true", help="Run the server only")
    parser.add_argument("--setup", action="store_true", help="Complete setup (install + init-db + run)")
    parser.add_argument("--with-browser", action="store_true", help="Open browser when running")

    args = parser.parse_args()

    # If no arguments provided, run complete setup
    if not any(vars(args).values()):
        setup_and_run()
    else:
        if args.install:
            install_dependencies()
        if args.init_db:
            initialize_database()
        if args.run or (args.with_browser and not any([args.install, args.init_db, args.setup])):
            if args.with_browser:
                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()

            run_server()
        if args.setup:
            setup_and_run()


if __name__ == "__main__":
    main()