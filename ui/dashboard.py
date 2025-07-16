"""
Main Dashboard for Hospital Management System
Central hub for all hospital management operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

from ui.patient_form import PatientForm
from ui.appointment_ui import AppointmentUI
from ui.doctor_ui import DoctorUI
from ui.opd_ui import OPDUI
from ui.patient_details import PatientDetails
from utils.file_io import PatientManager, AppointmentManager, DoctorManager, OPDManager
from utils.pdf_generator import PDFGenerator

class HospitalDashboard:
    def __init__(self, root):
        self.root = root
        self.setup_managers()
        self.setup_ui()
        self.refresh_dashboard_stats()
    
    def setup_managers(self):
        """Initialize all data managers"""
        self.patient_manager = PatientManager()
        self.appointment_manager = AppointmentManager()
        self.doctor_manager = DoctorManager()
        self.opd_manager = OPDManager()
        self.pdf_generator = PDFGenerator()
    
    def setup_styles(self):
        """Configure modern UI styles"""
        style = ttk.Style()
        
        # Configure modern color scheme
        style.configure('TFrame', background='#f8f9fa')
        style.configure('TLabel', background='#f8f9fa', foreground='#2c3e50', 
                       font=('Arial', 10))
        style.configure('TLabelFrame', background='#ffffff', relief='solid', borderwidth=1)
        style.configure('TLabelFrame.Label', background='#ffffff', foreground='#2c3e50', 
                       font=('Arial', 11, 'bold'))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=(15, 10))
        
        # Custom styles for specific elements
        style.configure('Header.TLabel', background='#2c3e50', foreground='white', 
                       font=('Arial', 24, 'bold'))
        style.configure('Subtitle.TLabel', background='#34495e', foreground='#ecf0f1',
                       font=('Arial', 11))
        style.configure('StatsTitle.TLabel', foreground='#2c3e50', font=('Arial', 10, 'bold'))
        style.configure('Nav.TButton', font=('Arial', 11, 'bold'), padding=(20, 15))
        style.configure('Quick.TButton', font=('Arial', 10), padding=(15, 10))
        
        # Map button styles with hover effects
        style.map('Nav.TButton',
                 background=[('active', '#3498db'), ('pressed', '#2980b9')])
        style.map('Quick.TButton',
                 background=[('active', '#2ecc71'), ('pressed', '#27ae60')])
        style.map('Accent.TButton',
                 background=[('active', '#2980b9'), ('pressed', '#21618c')])
    
    def create_header_section(self, parent):
        """Create enhanced header with logo and title"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Main title with medical cross symbol
        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(fill=tk.X)
        
        # Hospital icon (using Unicode medical symbol)
        icon_label = tk.Label(title_frame, text="⚕", font=('Arial', 36), 
                              bg='#2c3e50', fg='#e74c3c')
        icon_label.pack(side=tk.LEFT, padx=(20, 15), pady=10)
        
        # Title and subtitle
        text_frame = tk.Frame(title_frame, bg='#2c3e50')
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(text_frame, text="Kamane Hospital Management System",
                               bg='#2c3e50', fg='white', font=('Arial', 24, 'bold'))
        title_label.pack(anchor=tk.W, pady=(10, 0))
        
        subtitle_label = tk.Label(text_frame, text="Comprehensive Healthcare Administration Platform",
                                  bg='#34495e', fg='#ecf0f1', font=('Arial', 11))
        subtitle_label.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)
        
        # Current date/time
        current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")
        time_label = tk.Label(title_frame, text=current_time, 
                              bg='#2c3e50', fg='#bdc3c7',
                              font=('Arial', 10))
        time_label.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def setup_ui(self):
        """Setup the main dashboard UI"""
        # Configure styles
        self.setup_styles()
        
        # Main container with gradient-like background
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header section with logo and title
        self.create_header_section(main_frame)
        
        # Statistics frame
        self.create_stats_frame(main_frame)
        
        # Navigation buttons frame
        self.create_navigation_frame(main_frame)
        
        # Quick actions frame
        self.create_quick_actions_frame(main_frame)
        
        # Recent activities frame
        self.create_recent_activities_frame(main_frame)
    
    def create_stats_frame(self, parent):
        """Create enhanced statistics display frame"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Dashboard Statistics", 
                                   padding=20)
        stats_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Stats grid with modern cards
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Configure grid weights for responsive layout
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # Patient count card
        self.patient_count_var = tk.StringVar(value="0")
        patient_card = self.create_stat_card(stats_grid, "👥", "Total Patients", 
                                           self.patient_count_var, "#3498db", 0, 0)
        
        # Appointments today card
        self.appointments_today_var = tk.StringVar(value="0")
        apt_card = self.create_stat_card(stats_grid, "📅", "Appointments Today", 
                                       self.appointments_today_var, "#2ecc71", 0, 1)
        
        # OPD visits today card
        self.opd_today_var = tk.StringVar(value="0")
        opd_card = self.create_stat_card(stats_grid, "🏥", "OPD Visits Today", 
                                       self.opd_today_var, "#f39c12", 0, 2)
        
        # Doctors card
        self.doctor_count_var = tk.StringVar(value="0")
        doc_card = self.create_stat_card(stats_grid, "👨‍⚕️", "Total Doctors", 
                                       self.doctor_count_var, "#9b59b6", 0, 3)
    
    def create_stat_card(self, parent, icon, title, value_var, color, row, col):
        """Create a modern statistics card"""
        card_frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
        card_frame.grid(row=row, column=col, padx=15, pady=10, sticky='ew')
        
        # Icon
        icon_label = tk.Label(card_frame, text=icon, font=('Arial', 20),
                              bg='white', fg=color)
        icon_label.pack(pady=(15, 5))
        
        # Title
        title_label = tk.Label(card_frame, text=title, bg='white',
                               fg='#2c3e50', font=('Arial', 10, 'bold'))
        title_label.pack()
        
        # Value with colored background
        value_frame = tk.Frame(card_frame, bg='white')
        value_frame.pack(pady=(5, 15), padx=10, fill=tk.X)
        
        value_label = tk.Label(value_frame, textvariable=value_var,
                               font=('Arial', 24, 'bold'), fg=color,
                               bg='white', anchor='center')
        value_label.pack(fill=tk.X)
        
        return card_frame
    
    def create_navigation_frame(self, parent):
        """Create enhanced main navigation buttons"""
        nav_frame = ttk.LabelFrame(parent, text="🚀 Main Modules", 
                                 padding=25)
        nav_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Navigation buttons grid
        nav_grid = ttk.Frame(nav_frame)
        nav_grid.pack(fill=tk.X)
        
        # Configure grid weights for responsive layout
        for i in range(3):
            nav_grid.columnconfigure(i, weight=1)
        
        # First row of navigation buttons
        nav_buttons_row1 = [
            ("👤 Patient Management", self.open_patient_management, "Manage patient records and information"),
            ("📅 Appointments", self.open_appointments, "Schedule and manage appointments"),
            ("🏥 OPD Management", self.open_opd_management, "Handle outpatient department operations")
        ]
        
        for i, (text, command, tooltip) in enumerate(nav_buttons_row1):
            btn = ttk.Button(nav_grid, text=text, command=command, 
                           style='Nav.TButton', width=25)
            btn.grid(row=0, column=i, padx=15, pady=10, sticky='ew')
        
        # Second row of navigation buttons
        nav_buttons_row2 = [
            ("👨‍⚕️ Doctor Management", self.open_doctor_management, "Manage doctor profiles and schedules"),
            ("📊 Patient Details", self.open_patient_details, "View comprehensive patient information"),
            ("🔄 Refresh Dashboard", self.refresh_dashboard_stats, "Update dashboard statistics")
        ]
        
        for i, (text, command, tooltip) in enumerate(nav_buttons_row2):
            btn = ttk.Button(nav_grid, text=text, command=command, 
                           style='Nav.TButton', width=25)
            btn.grid(row=1, column=i, padx=15, pady=10, sticky='ew')
    
    def create_quick_actions_frame(self, parent):
        """Create enhanced quick action buttons"""
        quick_frame = ttk.LabelFrame(parent, text="⚡ Quick Actions", 
                                   padding=20)
        quick_frame.pack(fill=tk.X, pady=(0, 25))
        
        quick_grid = ttk.Frame(quick_frame)
        quick_grid.pack(fill=tk.X)
        
        # Configure grid weights for responsive layout
        for i in range(2):
            quick_grid.columnconfigure(i, weight=1)
        
        # Quick actions with icons
        quick_actions = [
            ("➕ Quick Patient Registration", self.quick_patient_registration),
            ("📝 Quick Appointment Booking", self.quick_appointment_booking),
            ("📈 Generate Reports", self.show_reports_menu),
            ("📁 Open PDF Folder", self.open_pdf_folder)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            row = i // 2
            col = i % 2
            btn = ttk.Button(quick_grid, text=text, command=command, 
                           style='Quick.TButton', width=30)
            btn.grid(row=row, column=col, padx=15, pady=10, sticky='ew')
    
    def create_recent_activities_frame(self, parent):
        """Create enhanced recent activities display"""
        recent_frame = ttk.LabelFrame(parent, text="📋 Recent Activities", 
                                    padding=15)
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        # Activities container with modern styling
        activities_container = ttk.Frame(recent_frame)
        activities_container.pack(fill=tk.BOTH, expand=True)
        
        # Recent activities text widget with enhanced styling
        self.recent_text = tk.Text(activities_container, height=10, width=90, 
                                  state=tk.DISABLED, wrap=tk.WORD,
                                  font=('Segoe UI', 10), bg='#ffffff',
                                  fg='#2c3e50', selectbackground='#3498db',
                                  relief='flat', borderwidth=0, padx=15, pady=10)
        
        scrollbar = ttk.Scrollbar(activities_container, orient=tk.VERTICAL, 
                                command=self.recent_text.yview)
        self.recent_text.config(yscrollcommand=scrollbar.set)
        
        # Pack with modern layout
        self.recent_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Auto-refresh button
        refresh_activities_btn = ttk.Button(recent_frame, text="🔄 Refresh Activities", 
                                          command=self.update_recent_activities,
                                          style='Quick.TButton')
        refresh_activities_btn.pack(pady=(10, 0))
        
        self.update_recent_activities()
    
    def refresh_dashboard_stats(self):
        """Refresh dashboard statistics"""
        try:
            # Patient count
            patients = self.patient_manager.get_all_patients()
            self.patient_count_var.set(str(len(patients)))
            
            # Appointments today
            today = datetime.now().strftime("%Y-%m-%d")
            today_appointments = self.appointment_manager.get_appointments_by_date(today)
            self.appointments_today_var.set(str(len(today_appointments)))
            
            # OPD visits today
            today_visits = self.opd_manager.get_todays_visits()
            self.opd_today_var.set(str(len(today_visits)))
            
            # Doctor count
            doctors = self.doctor_manager.get_all_doctors()
            self.doctor_count_var.set(str(len(doctors)))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing dashboard: {str(e)}")
    
    def update_recent_activities(self):
        """Update recent activities display"""
        try:
            self.recent_text.config(state=tk.NORMAL)
            self.recent_text.delete(1.0, tk.END)
            
            activities = []
            
            # Recent patients
            patients = self.patient_manager.get_all_patients()
            recent_patients = sorted(patients, key=lambda x: x.get('registration_date', ''), reverse=True)[:5]
            for patient in recent_patients:
                activities.append(f"Patient Registered: {patient.get('name', 'Unknown')} ({patient.get('id', 'Unknown')})")
            
            # Recent appointments
            appointments = self.appointment_manager.get_all_appointments()
            recent_appointments = sorted(appointments, key=lambda x: x.get('created_date', ''), reverse=True)[:5]
            for apt in recent_appointments:
                activities.append(f"Appointment Scheduled: {apt.get('patient_id', 'Unknown')} on {apt.get('appointment_date', 'Unknown')}")
            
            # Recent OPD visits
            visits = self.opd_manager.get_all_visits()
            recent_visits = sorted(visits, key=lambda x: f"{x.get('visit_date', '')} {x.get('visit_time', '')}", reverse=True)[:5]
            for visit in recent_visits:
                activities.append(f"OPD Visit: {visit.get('patient_id', 'Unknown')} on {visit.get('visit_date', 'Unknown')}")
            
            # Display activities
            if activities:
                for activity in activities[:10]:  # Show last 10 activities
                    self.recent_text.insert(tk.END, f"• {activity}\n")
            else:
                self.recent_text.insert(tk.END, "No recent activities found.")
            
            self.recent_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating recent activities: {str(e)}")
    
    def open_patient_management(self):
        """Open patient management window"""
        PatientForm(self.root)
    
    def open_appointments(self):
        """Open appointments window"""
        AppointmentUI(self.root)
    
    def open_opd_management(self):
        """Open OPD management window"""
        OPDUI(self.root)
    
    def open_doctor_management(self):
        """Open doctor management window"""
        DoctorUI(self.root)
    
    def open_patient_details(self):
        """Open patient details window"""
        PatientDetails(self.root)
    
    def quick_patient_registration(self):
        """Quick patient registration"""
        PatientForm(self.root, quick_mode=True)
    
    def quick_appointment_booking(self):
        """Quick appointment booking"""
        AppointmentUI(self.root, quick_mode=True)
    
    def show_reports_menu(self):
        """Show reports generation menu"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("Generate Reports")
        reports_window.geometry("400x300")
        reports_window.transient(self.root)
        reports_window.grab_set()
        
        # Center the window
        reports_window.update_idletasks()
        x = (reports_window.winfo_screenwidth() // 2) - (reports_window.winfo_width() // 2)
        y = (reports_window.winfo_screenheight() // 2) - (reports_window.winfo_height() // 2)
        reports_window.geometry(f'+{x}+{y}')
        
        ttk.Label(reports_window, text="Generate Reports", font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Report buttons
        ttk.Button(reports_window, text="All Appointments Report", 
                  command=lambda: self.generate_appointments_report(),
                  width=30).pack(pady=10)
        
        ttk.Button(reports_window, text="Today's Appointments Report", 
                  command=lambda: self.generate_appointments_report(datetime.now().strftime("%Y-%m-%d")),
                  width=30).pack(pady=10)
        
        ttk.Button(reports_window, text="All OPD Visits Report", 
                  command=lambda: self.generate_opd_report(),
                  width=30).pack(pady=10)
        
        ttk.Button(reports_window, text="Today's OPD Report", 
                  command=lambda: self.generate_opd_report(datetime.now().strftime("%Y-%m-%d")),
                  width=30).pack(pady=10)
        
        ttk.Button(reports_window, text="Close", 
                  command=reports_window.destroy,
                  width=30).pack(pady=20)
    
    def generate_appointments_report(self, date=None):
        """Generate appointments report"""
        try:
            if date is None:
                filepath = self.pdf_generator.generate_appointment_list()
            else:
                filepath = self.pdf_generator.generate_appointment_list(date)
            messagebox.showinfo("Success", f"Appointments report generated: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
    
    def generate_opd_report(self, date=None):
        """Generate OPD report"""
        try:
            if date is None:
                filepath = self.pdf_generator.generate_opd_report()
            else:
                filepath = self.pdf_generator.generate_opd_report(date)
            messagebox.showinfo("Success", f"OPD report generated: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
    
    def open_pdf_folder(self):
        """Open PDF folder in file explorer"""
        try:
            pdf_folder = os.path.abspath("generated_pdfs")
            if os.name == 'nt':  # Windows
                os.startfile(pdf_folder)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{pdf_folder}"' if sys.platform == 'darwin' else f'xdg-open "{pdf_folder}"')
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open PDF folder: {str(e)}")
