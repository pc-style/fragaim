#!/usr/bin/env python3
"""
    Unibot GUI Launcher
    Copyright (C) 2025 vike256
    
    Launches the Unibot GUI with proper path configuration for Windows.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the Unibot GUI"""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    # Change to src directory for relative imports to work
    os.chdir(src_path)
    
    try:
        # Import and run the GUI
        from gui import UnibotGUI
        
        print("Starting Unibot GUI...")
        app = UnibotGUI()
        app.run()
        
    except ImportError as e:
        print(f"Error: Failed to import GUI components: {e}")
        print("Make sure you're running this from the correct directory and all dependencies are installed.")
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()