import tkinter as tk
import sys

def main():
    """Main entry point for the application"""
    try:
        from .storage import Storage
        from .ui.main_window import MainWindow
        
        # Initialize storage
        storage = Storage()
        
        # Create and run the main window
        root = tk.Tk()
        app = MainWindow(root, storage)
        app.run()
        
    except ImportError as e:
        print(f"Error: {e}")
        print("Please make sure all dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
