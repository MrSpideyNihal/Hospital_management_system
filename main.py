"""
Hospital Management System - Main Application
A comprehensive offline desktop application for hospital management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.dashboard import HospitalDashboard
from utils.file_io import FileIOManager

class HospitalManagementApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_application()
        self.initialize_data_directories()
        self.create_dashboard()
    
    def setup_application(self):
        """Setup main application window with enhanced styling"""
        self.root.title("🏥 Hospital Management System")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Enhanced application styling
        self.root.configure(bg='#f8f9fa')
        
        # Configure window icon and appearance
        try:
            # Try to set a modern appearance
            self.root.tk.call('tk', 'scaling', 1.2)
        except:
            pass
        
        # Center the window on screen
        self.center_window()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure ttk theme for modern appearance
        self.setup_theme()
    
    def setup_theme(self):
        """Setup modern theme for the application"""
        try:
            import tkinter.ttk as ttk
            style = ttk.Style()
            
            # Try to use a modern theme if available
            available_themes = style.theme_names()
            modern_themes = ['vista', 'xpnative', 'winnative', 'clam', 'alt']
            
            for theme in modern_themes:
                if theme in available_themes:
                    style.theme_use(theme)
                    break
            
            # Configure modern colors
            style.configure('TLabel', background='#f8f9fa', foreground='#2c3e50')
            style.configure('TFrame', background='#f8f9fa')
            style.configure('TLabelFrame', background='#ffffff')
            
        except Exception:
            # Fall back to default theme if there's any issue
            pass
    
    def center_window(self):
        """Center the application window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def initialize_data_directories(self):
        """Create necessary directories and initialize data files"""
        directories = ['data', 'generated_pdfs']
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize data files if they don't exist
        file_io = FileIOManager()
        
        # Initialize empty data structures
        if not os.path.exists('data/patients.json'):
            file_io.save_data('data/patients.json', [])
        
        if not os.path.exists('data/appointments.json'):
            file_io.save_data('data/appointments.json', [])
        
        if not os.path.exists('data/doctors.json'):
            file_io.save_data('data/doctors.json', [])
        
        if not os.path.exists('data/opd_visits.json'):
            file_io.save_data('data/opd_visits.json', [])
    
    def create_dashboard(self):
        """Create and display the main dashboard"""
        self.dashboard = HospitalDashboard(self.root)
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the Hospital Management System?"):
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = HospitalManagementApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
