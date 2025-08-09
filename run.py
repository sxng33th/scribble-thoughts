#!/usr/bin/env python3
"""
Scribble Thoughts - A simple todo and clipboard manager

Run this script to start the application.
"""
import os
import sys

def get_base_path():
    """Get the base path for the application"""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def main():
    """Launch the application"""
    try:
        # Add the app directory to the path
        base_path = get_base_path()
        app_path = os.path.join(base_path, 'app')
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
            
        from app.__main__ import main as app_main
        app_main()
        
    except Exception as e:
        import traceback
        print("Error: Could not start the application.")
        print(f"Details: {e}")
        print("\nStack trace:")
        traceback.print_exc()
        print("\nPlease make sure all dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
