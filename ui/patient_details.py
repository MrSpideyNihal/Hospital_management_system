"""
Patient Details UI for Hospital Management System
Comprehensive view of patient information, history, appointments, and medical records
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

from utils.file_io import PatientManager, AppointmentManager, OPDManager, DoctorManager
from utils.pdf_generator import PDFGenerator

class PatientDetails:
    def __init__(self, parent):
        self.parent = parent
        self.patient_manager = PatientManager()
        self.appointment_manager = AppointmentManager()
        self.opd_manager = OPDManager()
        self.doctor_manager = DoctorManager()
        self.pdf_generator = PDFGenerator()
        self.current_patient = None
        
        self.create_window()
        self.setup_ui()
        self.load_patients()
    
    def create_window(self):
        """Create patient details window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Patient Details & History")
        self.window.geometry("1400x900")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f'+{x}+{y}')
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text="Patient Details & Medical History", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create paned window for patient selection and details
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Patient selection
        self.create_patient_selection_panel(paned)
        
        # Right panel - Patient details
        self.create_patient_details_panel(paned)
    
    def create_patient_selection_panel(self, parent):
        """Create patient selection panel"""
        selection_frame = ttk.LabelFrame(parent, text="Select Patient", padding=10)
        parent.add(selection_frame, weight=1)
        
        # Search frame
        search_frame = ttk.Frame(selection_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search Patient:").pack(anchor=tk.W)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=5)
        
        self.patient_search_var = tk.StringVar()
        self.patient_search_var.trace('w', self.on_patient_search)
        search_entry = ttk.Entry(search_input_frame, textvariable=self.patient_search_var, width=25)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(search_input_frame, text="Clear", 
                  command=self.clear_patient_search).pack(side=tk.LEFT)
        
        # Patient list
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Age", "Phone")
        self.patient_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        column_widths = {"ID": 80, "Name": 150, "Age": 60, "Phone": 120}
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=column_widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)
        
        self.patient_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.patient_tree.bind("<Button-1>", self.on_patient_select)
        self.patient_tree.bind("<Double-1>", self.on_patient_double_click)
        
        # Action buttons
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="View Details", 
                  command=self.view_selected_patient).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Generate PDF", 
                  command=self.generate_patient_pdf).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Refresh List", 
                  command=self.load_patients).pack(fill=tk.X, pady=2)
    
    def create_patient_details_panel(self, parent):
        """Create patient details panel"""
        details_frame = ttk.Frame(parent)
        parent.add(details_frame, weight=3)
        
        # Patient info header
        self.create_patient_info_header(details_frame)
        
        # Notebook for different sections
        notebook = ttk.Notebook(details_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Personal Information tab
        self.create_personal_info_tab(notebook)
        
        # Medical History tab
        self.create_medical_history_tab(notebook)
        
        # Appointments tab
        self.create_appointments_tab(notebook)
        
        # OPD Visits tab
        self.create_opd_visits_tab(notebook)
        
        # Payment History tab
        self.create_payment_history_tab(notebook)
    
    def create_patient_info_header(self, parent):
        """Create patient information header"""
        header_frame = ttk.LabelFrame(parent, text="Patient Summary", padding=15)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Patient basic info
        info_grid = ttk.Frame(header_frame)
        info_grid.pack(fill=tk.X)
        
        # Left column
        left_frame = ttk.Frame(info_grid)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.patient_name_var = tk.StringVar(value="No patient selected")
        self.patient_id_var = tk.StringVar(value="")
        self.patient_age_var = tk.StringVar(value="")
        self.patient_gender_var = tk.StringVar(value="")
        
        ttk.Label(left_frame, text="Name:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(left_frame, textvariable=self.patient_name_var, 
                 font=('Arial', 12, 'bold'), foreground='blue').grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(left_frame, text="Patient ID:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(left_frame, textvariable=self.patient_id_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Right column
        right_frame = ttk.Frame(info_grid)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Age:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(right_frame, textvariable=self.patient_age_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(right_frame, text="Gender:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(right_frame, textvariable=self.patient_gender_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Statistics
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.total_appointments_var = tk.StringVar(value="0")
        self.total_visits_var = tk.StringVar(value="0")
        self.last_visit_var = tk.StringVar(value="Never")
        
        # Stats grid
        ttk.Label(stats_frame, text="Total Appointments:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(stats_frame, textvariable=self.total_appointments_var, foreground='green').grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Total OPD Visits:", font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(20, 20))
        ttk.Label(stats_frame, textvariable=self.total_visits_var, foreground='blue').grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Last Visit:", font=('Arial', 9, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=(20, 20))
        ttk.Label(stats_frame, textvariable=self.last_visit_var, foreground='orange').grid(row=0, column=5, sticky=tk.W)
    
    def create_personal_info_tab(self, notebook):
        """Create personal information tab"""
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Personal Information")
        
        # Personal info container
        info_container = ttk.LabelFrame(info_frame, text="Patient Details", padding=20)
        info_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create scrollable frame
        canvas = tk.Canvas(info_container)
        scrollbar = ttk.Scrollbar(info_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Personal information fields
        self.personal_info_vars = {}
        fields = [
            ("Patient ID", "id"),
            ("Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Address", "address"),
            ("Blood Group", "blood_group"),
            ("Emergency Contact", "emergency_contact"),
            ("Registration Date", "registration_date"),
            ("Medical History", "medical_history")
        ]
        
        row = 0
        for label_text, field_name in fields:
            ttk.Label(scrollable_frame, text=f"{label_text}:", 
                     font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 20))
            
            self.personal_info_vars[field_name] = tk.StringVar()
            
            if field_name in ["address", "medical_history"]:
                # Text widget for long text
                text_widget = tk.Text(scrollable_frame, height=4, width=50, wrap=tk.WORD, state=tk.DISABLED)
                text_widget.grid(row=row, column=1, sticky=tk.W, pady=5)
                self.personal_info_vars[f"{field_name}_widget"] = text_widget
            else:
                # Label for regular text
                info_label = ttk.Label(scrollable_frame, textvariable=self.personal_info_vars[field_name], 
                                     wraplength=400, font=('Arial', 10))
                info_label.grid(row=row, column=1, sticky=tk.W, pady=5)
            
            row += 1
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_medical_history_tab(self, notebook):
        """Create medical history tab"""
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Medical History")
        
        # Medical history container
        history_container = ttk.LabelFrame(history_frame, text="Medical Records", padding=10)
        history_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Combined medical history from OPD visits
        columns = ("Date", "Doctor", "Diagnosis", "Treatment", "Prescription", "Notes")
        self.medical_history_tree = ttk.Treeview(history_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"Date": 100, "Doctor": 120, "Diagnosis": 150, "Treatment": 150, "Prescription": 150, "Notes": 150}
        for col in columns:
            self.medical_history_tree.heading(col, text=col)
            self.medical_history_tree.column(col, width=column_widths[col])
        
        # Scrollbars
        v_scrollbar_med = ttk.Scrollbar(history_container, orient=tk.VERTICAL, command=self.medical_history_tree.yview)
        h_scrollbar_med = ttk.Scrollbar(history_container, orient=tk.HORIZONTAL, command=self.medical_history_tree.xview)
        self.medical_history_tree.configure(yscrollcommand=v_scrollbar_med.set, xscrollcommand=h_scrollbar_med.set)
        
        self.medical_history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar_med.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar_med.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click for details
        self.medical_history_tree.bind("<Double-1>", self.show_medical_record_details)
    
    def create_appointments_tab(self, notebook):
        """Create appointments tab"""
        appointments_frame = ttk.Frame(notebook)
        notebook.add(appointments_frame, text="Appointments")
        
        # Filter frame
        filter_frame = ttk.Frame(appointments_frame)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.appointment_filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.appointment_filter_var,
                                  values=["All", "Scheduled", "Confirmed", "Completed", "Cancelled"],
                                  width=15, state="readonly")
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", self.filter_appointments)
        
        ttk.Button(filter_frame, text="Refresh", 
                  command=self.load_patient_appointments).pack(side=tk.LEFT, padx=20)
        
        # Appointments list
        appointments_container = ttk.LabelFrame(appointments_frame, text="Appointment History", padding=10)
        appointments_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Date", "Time", "Doctor", "Type", "Status", "Notes")
        self.appointments_tree = ttk.Treeview(appointments_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"ID": 80, "Date": 100, "Time": 80, "Doctor": 120, "Type": 120, "Status": 100, "Notes": 200}
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=column_widths[col])
        
        # Scrollbars
        v_scrollbar_apt = ttk.Scrollbar(appointments_container, orient=tk.VERTICAL, command=self.appointments_tree.yview)
        h_scrollbar_apt = ttk.Scrollbar(appointments_container, orient=tk.HORIZONTAL, command=self.appointments_tree.xview)
        self.appointments_tree.configure(yscrollcommand=v_scrollbar_apt.set, xscrollcommand=h_scrollbar_apt.set)
        
        self.appointments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar_apt.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar_apt.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click for details
        self.appointments_tree.bind("<Double-1>", self.show_appointment_details)
    
    def create_opd_visits_tab(self, notebook):
        """Create OPD visits tab"""
        visits_frame = ttk.Frame(notebook)
        notebook.add(visits_frame, text="OPD Visits")
        
        # Filter frame
        visit_filter_frame = ttk.Frame(visits_frame)
        visit_filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(visit_filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.visit_filter_var = tk.StringVar(value="All")
        visit_filter_combo = ttk.Combobox(visit_filter_frame, textvariable=self.visit_filter_var,
                                        values=["All", "Waiting", "In Progress", "Completed", "Cancelled"],
                                        width=15, state="readonly")
        visit_filter_combo.pack(side=tk.LEFT, padx=5)
        visit_filter_combo.bind("<<ComboboxSelected>>", self.filter_opd_visits)
        
        ttk.Button(visit_filter_frame, text="Refresh", 
                  command=self.load_patient_opd_visits).pack(side=tk.LEFT, padx=20)
        
        # OPD visits list
        visits_container = ttk.LabelFrame(visits_frame, text="OPD Visit History", padding=10)
        visits_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Date", "Time", "Doctor", "Type", "Priority", "Status", "Chief Complaint")
        self.opd_visits_tree = ttk.Treeview(visits_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"ID": 80, "Date": 100, "Time": 80, "Doctor": 120, "Type": 120, 
                        "Priority": 80, "Status": 100, "Chief Complaint": 200}
        for col in columns:
            self.opd_visits_tree.heading(col, text=col)
            self.opd_visits_tree.column(col, width=column_widths[col])
        
        # Scrollbars
        v_scrollbar_opd = ttk.Scrollbar(visits_container, orient=tk.VERTICAL, command=self.opd_visits_tree.yview)
        h_scrollbar_opd = ttk.Scrollbar(visits_container, orient=tk.HORIZONTAL, command=self.opd_visits_tree.xview)
        self.opd_visits_tree.configure(yscrollcommand=v_scrollbar_opd.set, xscrollcommand=h_scrollbar_opd.set)
        
        self.opd_visits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar_opd.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar_opd.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click for details
        self.opd_visits_tree.bind("<Double-1>", self.show_opd_visit_details)
    
    def create_payment_history_tab(self, notebook):
        """Create payment history tab"""
        payment_frame = ttk.Frame(notebook)
        notebook.add(payment_frame, text="Payment History")
        
        # Payment summary
        summary_frame = ttk.LabelFrame(payment_frame, text="Payment Summary", padding=15)
        summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill=tk.X)
        
        self.total_payments_var = tk.StringVar(value="₹0.00")
        self.pending_payments_var = tk.StringVar(value="₹0.00")
        self.last_payment_var = tk.StringVar(value="Never")
        
        ttk.Label(summary_grid, text="Total Paid:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(summary_grid, textvariable=self.total_payments_var, 
                 font=('Arial', 12, 'bold'), foreground='green').grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(summary_grid, text="Pending:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(40, 20))
        ttk.Label(summary_grid, textvariable=self.pending_payments_var, 
                 font=('Arial', 12, 'bold'), foreground='red').grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(summary_grid, text="Last Payment:", font=('Arial', 10, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=(40, 20))
        ttk.Label(summary_grid, textvariable=self.last_payment_var, foreground='blue').grid(row=0, column=5, sticky=tk.W)
        
        # Payment history list
        payment_container = ttk.LabelFrame(payment_frame, text="Payment Details", padding=10)
        payment_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Date", "Visit/Appointment", "Service", "Amount", "Payment Method", "Status")
        self.payment_tree = ttk.Treeview(payment_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"Date": 100, "Visit/Appointment": 120, "Service": 150, 
                        "Amount": 100, "Payment Method": 120, "Status": 100}
        for col in columns:
            self.payment_tree.heading(col, text=col)
            self.payment_tree.column(col, width=column_widths[col])
        
        # Scrollbars
        v_scrollbar_pay = ttk.Scrollbar(payment_container, orient=tk.VERTICAL, command=self.payment_tree.yview)
        h_scrollbar_pay = ttk.Scrollbar(payment_container, orient=tk.HORIZONTAL, command=self.payment_tree.xview)
        self.payment_tree.configure(yscrollcommand=v_scrollbar_pay.set, xscrollcommand=h_scrollbar_pay.set)
        
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar_pay.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar_pay.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_patients(self):
        """Load patients into selection list"""
        try:
            # Clear existing items
            for item in self.patient_tree.get_children():
                self.patient_tree.delete(item)
            
            # Load patients
            patients = self.patient_manager.get_all_patients()
            
            for patient in patients:
                self.patient_tree.insert("", tk.END, values=(
                    patient.get("id", ""),
                    patient.get("name", ""),
                    patient.get("age", ""),
                    patient.get("phone", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patients: {str(e)}")
    
    def on_patient_search(self, *args):
        """Handle patient search"""
        search_query = self.patient_search_var.get().strip()
        
        try:
            # Clear existing items
            for item in self.patient_tree.get_children():
                self.patient_tree.delete(item)
            
            # Search patients
            if search_query:
                patients = self.patient_manager.search_patients(search_query)
            else:
                patients = self.patient_manager.get_all_patients()
            
            # Populate tree
            for patient in patients:
                self.patient_tree.insert("", tk.END, values=(
                    patient.get("id", ""),
                    patient.get("name", ""),
                    patient.get("age", ""),
                    patient.get("phone", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching patients: {str(e)}")
    
    def clear_patient_search(self):
        """Clear patient search"""
        self.patient_search_var.set("")
    
    def on_patient_select(self, event):
        """Handle patient selection"""
        selection = self.patient_tree.selection()
        if selection:
            item = self.patient_tree.item(selection[0])
            patient_id = item['values'][0]
            self.load_patient_details(patient_id)
    
    def on_patient_double_click(self, event):
        """Handle patient double-click"""
        self.view_selected_patient()
    
    def view_selected_patient(self):
        """View selected patient details"""
        selection = self.patient_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient!")
            return
        
        item = self.patient_tree.item(selection[0])
        patient_id = item['values'][0]
        self.load_patient_details(patient_id)
    
    def load_patient_details(self, patient_id):
        """Load comprehensive patient details"""
        try:
            # Get patient data
            patient = self.patient_manager.get_patient_by_id(patient_id)
            if not patient:
                messagebox.showerror("Error", "Patient not found!")
                return
            
            self.current_patient = patient
            
            # Update header information
            self.patient_name_var.set(patient.get('name', 'Unknown'))
            self.patient_id_var.set(patient.get('id', ''))
            self.patient_age_var.set(patient.get('age', ''))
            self.patient_gender_var.set(patient.get('gender', ''))
            
            # Load personal information
            self.load_personal_information(patient)
            
            # Load medical history, appointments, and visits
            self.load_patient_appointments()
            self.load_patient_opd_visits()
            self.load_medical_history()
            self.load_payment_history()
            
            # Update statistics
            self.update_patient_statistics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patient details: {str(e)}")
    
    def load_personal_information(self, patient):
        """Load personal information"""
        try:
            for field_name, var in self.personal_info_vars.items():
                if field_name.endswith("_widget"):
                    # Handle text widgets
                    widget = var
                    field_name = field_name.replace("_widget", "")
                    widget.config(state=tk.NORMAL)
                    widget.delete("1.0", tk.END)
                    widget.insert("1.0", patient.get(field_name, "Not provided"))
                    widget.config(state=tk.DISABLED)
                elif isinstance(var, tk.StringVar):
                    var.set(patient.get(field_name, "Not provided"))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error loading personal information: {str(e)}")
    
    def load_patient_appointments(self):
        """Load patient appointments"""
        if not self.current_patient:
            return
        
        try:
            # Clear existing items
            for item in self.appointments_tree.get_children():
                self.appointments_tree.delete(item)
            
            # Get appointments
            appointments = self.appointment_manager.get_appointments_by_patient(self.current_patient['id'])
            
            # Apply filter
            filter_status = self.appointment_filter_var.get()
            if filter_status != "All":
                appointments = [apt for apt in appointments if apt.get('status') == filter_status]
            
            # Sort by date (newest first)
            appointments.sort(key=lambda x: x.get('appointment_date', ''), reverse=True)
            
            for appointment in appointments:
                self.appointments_tree.insert("", tk.END, values=(
                    appointment.get("id", ""),
                    appointment.get("appointment_date", ""),
                    appointment.get("appointment_time", ""),
                    appointment.get("doctor_name", appointment.get("doctor_id", "")),
                    appointment.get("appointment_type", ""),
                    appointment.get("status", ""),
                    appointment.get("notes", "")[:50] + "..." if len(appointment.get("notes", "")) > 50 else appointment.get("notes", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading appointments: {str(e)}")
    
    def load_patient_opd_visits(self):
        """Load patient OPD visits"""
        if not self.current_patient:
            return
        
        try:
            # Clear existing items
            for item in self.opd_visits_tree.get_children():
                self.opd_visits_tree.delete(item)
            
            # Get visits
            visits = self.opd_manager.get_visits_by_patient(self.current_patient['id'])
            
            # Apply filter
            filter_status = self.visit_filter_var.get()
            if filter_status != "All":
                visits = [visit for visit in visits if visit.get('status') == filter_status]
            
            # Sort by date (newest first)
            visits.sort(key=lambda x: f"{x.get('visit_date', '')} {x.get('visit_time', '')}", reverse=True)
            
            for visit in visits:
                self.opd_visits_tree.insert("", tk.END, values=(
                    visit.get("id", ""),
                    visit.get("visit_date", ""),
                    visit.get("visit_time", ""),
                    visit.get("doctor_name", visit.get("doctor_id", "")),
                    visit.get("visit_type", ""),
                    visit.get("priority", ""),
                    visit.get("status", ""),
                    visit.get("chief_complaint", "")[:50] + "..." if len(visit.get("chief_complaint", "")) > 50 else visit.get("chief_complaint", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading OPD visits: {str(e)}")
    
    def load_medical_history(self):
        """Load medical history from OPD visits"""
        if not self.current_patient:
            return
        
        try:
            # Clear existing items
            for item in self.medical_history_tree.get_children():
                self.medical_history_tree.delete(item)
            
            # Get visits with medical information
            visits = self.opd_manager.get_visits_by_patient(self.current_patient['id'])
            
            # Filter visits with medical data
            medical_visits = [v for v in visits if v.get('diagnosis') or v.get('treatment') or v.get('prescription')]
            
            # Sort by date (newest first)
            medical_visits.sort(key=lambda x: f"{x.get('visit_date', '')} {x.get('visit_time', '')}", reverse=True)
            
            for visit in medical_visits:
                self.medical_history_tree.insert("", tk.END, values=(
                    visit.get("visit_date", ""),
                    visit.get("doctor_name", visit.get("doctor_id", "")),
                    visit.get("diagnosis", "")[:100] + "..." if len(visit.get("diagnosis", "")) > 100 else visit.get("diagnosis", ""),
                    visit.get("treatment", "")[:100] + "..." if len(visit.get("treatment", "")) > 100 else visit.get("treatment", ""),
                    visit.get("prescription", "")[:100] + "..." if len(visit.get("prescription", "")) > 100 else visit.get("prescription", ""),
                    visit.get("notes", "")[:100] + "..." if len(visit.get("notes", "")) > 100 else visit.get("notes", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading medical history: {str(e)}")
    
    def load_payment_history(self):
        """Load payment history"""
        if not self.current_patient:
            return
        
        try:
            # Clear existing items
            for item in self.payment_tree.get_children():
                self.payment_tree.delete(item)
            
            # Get payments from OPD visits and appointments
            visits = self.opd_manager.get_visits_by_patient(self.current_patient['id'])
            appointments = self.appointment_manager.get_appointments_by_patient(self.current_patient['id'])
            
            payments = []
            total_paid = 0
            
            # Extract payments from visits
            for visit in visits:
                payment_amount = visit.get('payment_amount', '')
                if payment_amount:
                    try:
                        amount = float(payment_amount)
                        total_paid += amount
                        payments.append({
                            'date': visit.get('visit_date', ''),
                            'type': f"OPD Visit ({visit.get('id', '')})",
                            'service': visit.get('visit_type', 'OPD Consultation'),
                            'amount': f"₹{amount:.2f}",
                            'method': 'Cash',  # Default
                            'status': 'Paid'
                        })
                    except ValueError:
                        pass
            
            # Sort payments by date (newest first)
            payments.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Update payment summary
            self.total_payments_var.set(f"₹{total_paid:.2f}")
            self.pending_payments_var.set("₹0.00")  # Would need to calculate based on pending appointments
            
            if payments:
                latest_payment = max(payments, key=lambda x: x.get('date', ''))
                self.last_payment_var.set(latest_payment.get('date', 'Never'))
            else:
                self.last_payment_var.set("Never")
            
            # Populate payment tree
            for payment in payments:
                self.payment_tree.insert("", tk.END, values=(
                    payment.get("date", ""),
                    payment.get("type", ""),
                    payment.get("service", ""),
                    payment.get("amount", ""),
                    payment.get("method", ""),
                    payment.get("status", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading payment history: {str(e)}")
    
    def update_patient_statistics(self):
        """Update patient statistics"""
        if not self.current_patient:
            return
        
        try:
            # Get statistics
            appointments = self.appointment_manager.get_appointments_by_patient(self.current_patient['id'])
            visits = self.opd_manager.get_visits_by_patient(self.current_patient['id'])
            
            # Update counts
            self.total_appointments_var.set(str(len(appointments)))
            self.total_visits_var.set(str(len(visits)))
            
            # Find last visit
            all_visits = visits + appointments
            if all_visits:
                # Sort by date
                dated_visits = []
                for visit in all_visits:
                    visit_date = visit.get('visit_date') or visit.get('appointment_date')
                    if visit_date:
                        dated_visits.append((visit_date, visit))
                
                if dated_visits:
                    dated_visits.sort(key=lambda x: x[0], reverse=True)
                    last_visit_date = dated_visits[0][0]
                    self.last_visit_var.set(last_visit_date)
                else:
                    self.last_visit_var.set("Never")
            else:
                self.last_visit_var.set("Never")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating statistics: {str(e)}")
    
    def filter_appointments(self, event=None):
        """Filter appointments by status"""
        self.load_patient_appointments()
    
    def filter_opd_visits(self, event=None):
        """Filter OPD visits by status"""
        self.load_patient_opd_visits()
    
    def show_appointment_details(self, event):
        """Show appointment details"""
        selection = self.appointments_tree.selection()
        if not selection:
            return
        
        item = self.appointments_tree.item(selection[0])
        appointment_id = item['values'][0]
        
        # Find appointment details
        appointments = self.appointment_manager.get_all_appointments()
        appointment = next((a for a in appointments if a.get('id') == appointment_id), None)
        
        if appointment:
            self.show_details_window("Appointment Details", appointment, "appointment")
    
    def show_opd_visit_details(self, event):
        """Show OPD visit details"""
        selection = self.opd_visits_tree.selection()
        if not selection:
            return
        
        item = self.opd_visits_tree.item(selection[0])
        visit_id = item['values'][0]
        
        # Find visit details
        visits = self.opd_manager.get_all_visits()
        visit = next((v for v in visits if v.get('id') == visit_id), None)
        
        if visit:
            self.show_details_window("OPD Visit Details", visit, "opd_visit")
    
    def show_medical_record_details(self, event):
        """Show medical record details"""
        selection = self.medical_history_tree.selection()
        if not selection:
            return
        
        item = self.medical_history_tree.item(selection[0])
        visit_date = item['values'][0]
        doctor_name = item['values'][1]
        
        # Find the corresponding visit
        visits = self.opd_manager.get_visits_by_patient(self.current_patient['id'])
        visit = next((v for v in visits if v.get('visit_date') == visit_date and 
                     v.get('doctor_name') == doctor_name), None)
        
        if visit:
            self.show_details_window("Medical Record Details", visit, "medical_record")
    
    def show_details_window(self, title, data, data_type):
        """Show details in a separate window"""
        details_window = tk.Toplevel(self.window)
        details_window.title(title)
        details_window.geometry("600x700")
        details_window.transient(self.window)
        details_window.grab_set()
        
        # Center the window
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (details_window.winfo_width() // 2)
        y = (details_window.winfo_screenheight() // 2) - (details_window.winfo_height() // 2)
        details_window.geometry(f'+{x}+{y}')
        
        # Create scrollable frame
        canvas = tk.Canvas(details_window)
        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Details frame
        details_frame = ttk.LabelFrame(scrollable_frame, text=title, padding=20)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Display data based on type
        if data_type == "appointment":
            fields = [
                ("Appointment ID", "id"),
                ("Patient ID", "patient_id"),
                ("Patient Name", "patient_name"),
                ("Doctor ID", "doctor_id"),
                ("Doctor Name", "doctor_name"),
                ("Date", "appointment_date"),
                ("Time", "appointment_time"),
                ("Type", "appointment_type"),
                ("Status", "status"),
                ("Notes", "notes")
            ]
        elif data_type == "opd_visit":
            fields = [
                ("Visit ID", "id"),
                ("Patient ID", "patient_id"),
                ("Patient Name", "patient_name"),
                ("Doctor ID", "doctor_id"),
                ("Doctor Name", "doctor_name"),
                ("Visit Date", "visit_date"),
                ("Visit Time", "visit_time"),
                ("Visit Type", "visit_type"),
                ("Priority", "priority"),
                ("Status", "status"),
                ("Chief Complaint", "chief_complaint"),
                ("Diagnosis", "diagnosis"),
                ("Treatment", "treatment"),
                ("Prescription", "prescription"),
                ("Follow-up Date", "followup_date"),
                ("Payment Amount", "payment_amount"),
                ("Notes", "notes")
            ]
        else:  # medical_record
            fields = [
                ("Visit Date", "visit_date"),
                ("Doctor", "doctor_name"),
                ("Chief Complaint", "chief_complaint"),
                ("Diagnosis", "diagnosis"),
                ("Treatment", "treatment"),
                ("Prescription", "prescription"),
                ("Follow-up Date", "followup_date"),
                ("Notes", "notes")
            ]
        
        row = 0
        for label_text, field_name in fields:
            ttk.Label(details_frame, text=f"{label_text}:", 
                     font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 20))
            
            value = data.get(field_name, "N/A")
            if field_name in ["notes", "chief_complaint", "diagnosis", "treatment", "prescription"] and len(str(value)) > 50:
                # Use text widget for long text
                text_widget = tk.Text(details_frame, height=4, width=50, wrap=tk.WORD)
                text_widget.insert("1.0", str(value))
                text_widget.config(state=tk.DISABLED)
                text_widget.grid(row=row, column=1, sticky=tk.W, pady=5)
            else:
                # Use label for short text
                value_label = ttk.Label(details_frame, text=str(value), wraplength=400)
                value_label.grid(row=row, column=1, sticky=tk.W, pady=5)
            
            row += 1
        
        # Close button
        ttk.Button(details_frame, text="Close", 
                  command=details_window.destroy).grid(row=row, column=0, columnspan=2, pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def generate_patient_pdf(self):
        """Generate PDF for selected patient"""
        if not self.current_patient:
            messagebox.showwarning("Warning", "Please select a patient first!")
            return
        
        try:
            filepath = self.pdf_generator.generate_patient_summary(self.current_patient['id'])
            messagebox.showinfo("Success", f"Patient PDF generated successfully!\n\nFile: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF: {str(e)}")
