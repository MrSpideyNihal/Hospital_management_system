"""
OPD (Out Patient Department) Management UI for Hospital Management System
Handles patient check-ins, visits, queue management, and OPD operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import re

from utils.file_io import OPDManager, PatientManager, DoctorManager

class OPDUI:
    def __init__(self, parent):
        self.parent = parent
        self.opd_manager = OPDManager()
        self.patient_manager = PatientManager()
        self.doctor_manager = DoctorManager()
        self.current_visit_id = None
        
        self.create_window()
        self.setup_ui()
        self.load_visits()
    
    def create_window(self):
        """Create OPD management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("OPD Management")
        self.window.geometry("1200x800")
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
        ttk.Label(main_frame, text="OPD Management", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Quick check-in tab
        self.create_checkin_tab(notebook)
        
        # Visit form tab
        self.create_visit_form_tab(notebook)
        
        # Visit list tab
        self.create_visit_list_tab(notebook)
        
        # Queue management tab
        self.create_queue_tab(notebook)
    
    def create_checkin_tab(self, notebook):
        """Create quick check-in tab"""
        checkin_frame = ttk.Frame(notebook)
        notebook.add(checkin_frame, text="Quick Check-in")
        
        # Check-in container
        checkin_container = ttk.LabelFrame(checkin_frame, text="Patient Check-in", padding=20)
        checkin_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Patient search
        search_frame = ttk.Frame(checkin_container)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(search_frame, text="Search Patient:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        patient_search_frame = ttk.Frame(search_frame)
        patient_search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(patient_search_frame, text="Patient ID or Name:").pack(side=tk.LEFT, padx=(0, 10))
        self.checkin_search_var = tk.StringVar()
        self.checkin_search_var.trace('w', self.on_checkin_search)
        ttk.Entry(patient_search_frame, textvariable=self.checkin_search_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(patient_search_frame, text="Search", 
                  command=self.search_patients_for_checkin).pack(side=tk.LEFT, padx=5)
        
        # Patient selection list
        patient_list_frame = ttk.LabelFrame(checkin_container, text="Select Patient", padding=10)
        patient_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        columns = ("ID", "Name", "Age", "Phone", "Registration Date")
        self.checkin_patient_tree = ttk.Treeview(patient_list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.checkin_patient_tree.heading(col, text=col)
            self.checkin_patient_tree.column(col, width=120)
        
        # Scrollbar for patient list
        patient_scrollbar = ttk.Scrollbar(patient_list_frame, orient=tk.VERTICAL, command=self.checkin_patient_tree.yview)
        self.checkin_patient_tree.configure(yscrollcommand=patient_scrollbar.set)
        
        self.checkin_patient_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        patient_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind patient selection
        self.checkin_patient_tree.bind("<Double-1>", self.on_checkin_patient_select)
        
        # Quick check-in form
        quick_form_frame = ttk.LabelFrame(checkin_container, text="Quick Check-in Details", padding=10)
        quick_form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Selected patient info
        self.selected_patient_var = tk.StringVar(value="No patient selected")
        ttk.Label(quick_form_frame, text="Selected Patient:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Label(quick_form_frame, textvariable=self.selected_patient_var, 
                 font=('Arial', 10, 'bold'), foreground='blue').grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Chief complaint
        ttk.Label(quick_form_frame, text="Chief Complaint*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.quick_complaint_text = tk.Text(quick_form_frame, height=3, width=50)
        self.quick_complaint_text.grid(row=1, column=1, sticky=tk.W, pady=5, columnspan=2)
        
        # Priority
        ttk.Label(quick_form_frame, text="Priority:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.quick_priority_var = tk.StringVar(value="Normal")
        priority_combo = ttk.Combobox(quick_form_frame, textvariable=self.quick_priority_var,
                                    values=["Low", "Normal", "High", "Emergency"], width=20, state="readonly")
        priority_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Check-in buttons
        checkin_buttons_frame = ttk.Frame(checkin_container)
        checkin_buttons_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(checkin_buttons_frame, text="Quick Check-in", 
                  command=self.quick_checkin, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(checkin_buttons_frame, text="Clear Selection", 
                  command=self.clear_checkin_selection).pack(side=tk.LEFT, padx=5)
        
        # Load all patients initially
        self.load_patients_for_checkin()
    
    def create_visit_form_tab(self, notebook):
        """Create detailed visit form tab"""
        form_frame = ttk.Frame(notebook)
        notebook.add(form_frame, text="Visit Details")
        
        # Form container
        form_container = ttk.LabelFrame(form_frame, text="OPD Visit Information", padding=20)
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Form fields
        self.visit_form_vars = {}
        row = 0
        
        # Patient selection
        ttk.Label(form_container, text="Patient*:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["patient_id"] = tk.StringVar()
        patient_combo = ttk.Combobox(form_container, textvariable=self.visit_form_vars["patient_id"],
                                   width=50, state="readonly")
        patient_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        self.visit_patient_combo = patient_combo
        row += 1
        
        # Doctor selection
        ttk.Label(form_container, text="Doctor:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["doctor_id"] = tk.StringVar()
        doctor_combo = ttk.Combobox(form_container, textvariable=self.visit_form_vars["doctor_id"],
                                  width=50, state="readonly")
        doctor_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        self.visit_doctor_combo = doctor_combo
        row += 1
        
        # Visit type
        ttk.Label(form_container, text="Visit Type:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["visit_type"] = tk.StringVar(value="OPD Consultation")
        visit_type_combo = ttk.Combobox(form_container, textvariable=self.visit_form_vars["visit_type"],
                                      values=["OPD Consultation", "Follow-up", "Emergency", "Routine Check-up",
                                             "Specialist Consultation", "Diagnostic"], width=30)
        visit_type_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Priority
        ttk.Label(form_container, text="Priority:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["priority"] = tk.StringVar(value="Normal")
        priority_combo = ttk.Combobox(form_container, textvariable=self.visit_form_vars["priority"],
                                    values=["Low", "Normal", "High", "Emergency"], width=20, state="readonly")
        priority_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Status
        ttk.Label(form_container, text="Status:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["status"] = tk.StringVar(value="Waiting")
        status_combo = ttk.Combobox(form_container, textvariable=self.visit_form_vars["status"],
                                  values=["Waiting", "In Progress", "Completed", "Cancelled"], width=20, state="readonly")
        status_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Chief complaint
        ttk.Label(form_container, text="Chief Complaint*:").grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 10))
        self.chief_complaint_text = tk.Text(form_container, height=4, width=60)
        self.chief_complaint_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Diagnosis
        ttk.Label(form_container, text="Diagnosis:").grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 10))
        self.diagnosis_text = tk.Text(form_container, height=4, width=60)
        self.diagnosis_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Treatment
        ttk.Label(form_container, text="Treatment:").grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 10))
        self.treatment_text = tk.Text(form_container, height=4, width=60)
        self.treatment_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Prescription
        ttk.Label(form_container, text="Prescription:").grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 10))
        self.prescription_text = tk.Text(form_container, height=4, width=60)
        self.prescription_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Follow-up date
        ttk.Label(form_container, text="Follow-up Date:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["followup_date"] = tk.StringVar()
        ttk.Entry(form_container, textvariable=self.visit_form_vars["followup_date"], width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(form_container, text="(YYYY-MM-DD)").grid(row=row, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Payment amount
        ttk.Label(form_container, text="Payment Amount:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.visit_form_vars["payment_amount"] = tk.StringVar()
        ttk.Entry(form_container, textvariable=self.visit_form_vars["payment_amount"], width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Notes
        ttk.Label(form_container, text="Notes:").grid(row=row, column=0, sticky=tk.NW, pady=5, padx=(0, 10))
        self.visit_notes_text = tk.Text(form_container, height=3, width=60)
        self.visit_notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Form buttons
        form_buttons_frame = ttk.Frame(form_container)
        form_buttons_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(form_buttons_frame, text="Save Visit", 
                  command=self.save_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(form_buttons_frame, text="Update Visit", 
                  command=self.update_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(form_buttons_frame, text="Clear Form", 
                  command=self.clear_visit_form).pack(side=tk.LEFT, padx=5)
        
        # Load combo data
        self.load_visit_combo_data()
    
    def create_visit_list_tab(self, notebook):
        """Create visit list tab"""
        list_frame = ttk.Frame(notebook)
        notebook.add(list_frame, text="Visit List")
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Date filter
        ttk.Label(filter_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        self.date_filter_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_frame, textvariable=self.date_filter_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(20, 5))
        self.visit_status_filter_var = tk.StringVar(value="All")
        status_filter = ttk.Combobox(filter_frame, textvariable=self.visit_status_filter_var,
                                   values=["All", "Waiting", "In Progress", "Completed", "Cancelled"],
                                   width=15, state="readonly")
        status_filter.pack(side=tk.LEFT, padx=5)
        status_filter.bind("<<ComboboxSelected>>", self.on_visit_status_filter)
        
        # Search
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.visit_search_var = tk.StringVar()
        self.visit_search_var.trace('w', self.on_visit_search)
        ttk.Entry(filter_frame, textvariable=self.visit_search_var, width=25).pack(side=tk.LEFT, padx=5)
        
        # Filter buttons
        ttk.Button(filter_frame, text="Filter by Date", 
                  command=self.filter_visits_by_date).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_frame, text="Show All", 
                  command=self.load_visits).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Today's Visits", 
                  command=self.show_todays_visits).pack(side=tk.LEFT, padx=5)
        
        # Visit list
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Patient", "Doctor", "Visit Date", "Time", "Type", "Priority", "Status")
        self.visit_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"ID": 80, "Patient": 150, "Doctor": 120, "Visit Date": 100, 
                        "Time": 80, "Type": 120, "Priority": 80, "Status": 100}
        
        for col in columns:
            self.visit_tree.heading(col, text=col)
            self.visit_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.visit_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.visit_tree.xview)
        self.visit_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.visit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.visit_tree.bind("<Double-1>", self.on_visit_select)
        self.visit_tree.bind("<Button-3>", self.show_visit_context_menu)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(action_frame, text="Edit Visit", 
                  command=self.edit_selected_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Mark Complete", 
                  command=self.mark_visit_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel Visit", 
                  command=self.cancel_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Visit", 
                  command=self.delete_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh", 
                  command=self.load_visits).pack(side=tk.LEFT, padx=5)
    
    def create_queue_tab(self, notebook):
        """Create queue management tab"""
        queue_frame = ttk.Frame(notebook)
        notebook.add(queue_frame, text="Queue Management")
        
        # Queue stats
        stats_frame = ttk.LabelFrame(queue_frame, text="Queue Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Waiting patients
        self.waiting_count_var = tk.StringVar(value="0")
        waiting_frame = ttk.Frame(stats_grid)
        waiting_frame.grid(row=0, column=0, padx=20, pady=5)
        ttk.Label(waiting_frame, text="Waiting Patients", font=('Arial', 10, 'bold')).pack()
        ttk.Label(waiting_frame, textvariable=self.waiting_count_var, 
                 font=('Arial', 16, 'bold'), foreground='orange').pack()
        
        # In progress
        self.inprogress_count_var = tk.StringVar(value="0")
        progress_frame = ttk.Frame(stats_grid)
        progress_frame.grid(row=0, column=1, padx=20, pady=5)
        ttk.Label(progress_frame, text="In Progress", font=('Arial', 10, 'bold')).pack()
        ttk.Label(progress_frame, textvariable=self.inprogress_count_var, 
                 font=('Arial', 16, 'bold'), foreground='blue').pack()
        
        # Completed today
        self.completed_count_var = tk.StringVar(value="0")
        completed_frame = ttk.Frame(stats_grid)
        completed_frame.grid(row=0, column=2, padx=20, pady=5)
        ttk.Label(completed_frame, text="Completed Today", font=('Arial', 10, 'bold')).pack()
        ttk.Label(completed_frame, textvariable=self.completed_count_var, 
                 font=('Arial', 16, 'bold'), foreground='green').pack()
        
        # Priority queue
        priority_frame = ttk.LabelFrame(queue_frame, text="Priority Queue", padding=10)
        priority_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Priority queue list
        priority_columns = ("Position", "Patient", "Priority", "Chief Complaint", "Wait Time", "Action")
        self.priority_tree = ttk.Treeview(priority_frame, columns=priority_columns, show="headings", height=15)
        
        for col in priority_columns:
            self.priority_tree.heading(col, text=col)
            if col == "Position":
                self.priority_tree.column(col, width=80)
            elif col == "Patient":
                self.priority_tree.column(col, width=150)
            elif col == "Priority":
                self.priority_tree.column(col, width=100)
            elif col == "Chief Complaint":
                self.priority_tree.column(col, width=200)
            else:
                self.priority_tree.column(col, width=120)
        
        # Priority queue scrollbar
        priority_scrollbar = ttk.Scrollbar(priority_frame, orient=tk.VERTICAL, command=self.priority_tree.yview)
        self.priority_tree.configure(yscrollcommand=priority_scrollbar.set)
        
        self.priority_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        priority_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Queue management buttons
        queue_buttons_frame = ttk.Frame(queue_frame)
        queue_buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(queue_buttons_frame, text="Move to In Progress", 
                  command=self.move_to_inprogress).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_buttons_frame, text="Move Up in Queue", 
                  command=self.move_up_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_buttons_frame, text="Move Down in Queue", 
                  command=self.move_down_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_buttons_frame, text="Refresh Queue", 
                  command=self.refresh_queue).pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh queue
        self.refresh_queue()
    
    def load_patients_for_checkin(self):
        """Load patients for check-in"""
        try:
            # Clear existing items
            for item in self.checkin_patient_tree.get_children():
                self.checkin_patient_tree.delete(item)
            
            # Load patients
            patients = self.patient_manager.get_all_patients()
            
            for patient in patients:
                self.checkin_patient_tree.insert("", tk.END, values=(
                    patient.get("id", ""),
                    patient.get("name", ""),
                    patient.get("age", ""),
                    patient.get("phone", ""),
                    patient.get("registration_date", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patients: {str(e)}")
    
    def on_checkin_search(self, *args):
        """Handle check-in patient search"""
        self.search_patients_for_checkin()
    
    def search_patients_for_checkin(self):
        """Search patients for check-in"""
        search_query = self.checkin_search_var.get().strip()
        
        try:
            # Clear existing items
            for item in self.checkin_patient_tree.get_children():
                self.checkin_patient_tree.delete(item)
            
            # Search patients
            if search_query:
                patients = self.patient_manager.search_patients(search_query)
            else:
                patients = self.patient_manager.get_all_patients()
            
            # Populate tree
            for patient in patients:
                self.checkin_patient_tree.insert("", tk.END, values=(
                    patient.get("id", ""),
                    patient.get("name", ""),
                    patient.get("age", ""),
                    patient.get("phone", ""),
                    patient.get("registration_date", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching patients: {str(e)}")
    
    def on_checkin_patient_select(self, event):
        """Handle patient selection for check-in"""
        selection = self.checkin_patient_tree.selection()
        if selection:
            item = self.checkin_patient_tree.item(selection[0])
            patient_id = item['values'][0]
            patient_name = item['values'][1]
            self.selected_patient_var.set(f"{patient_id} - {patient_name}")
    
    def clear_checkin_selection(self):
        """Clear check-in selection"""
        self.selected_patient_var.set("No patient selected")
        self.quick_complaint_text.delete("1.0", tk.END)
        self.quick_priority_var.set("Normal")
        
        # Clear tree selection
        for item in self.checkin_patient_tree.selection():
            self.checkin_patient_tree.selection_remove(item)
    
    def quick_checkin(self):
        """Perform quick check-in"""
        selected_patient = self.selected_patient_var.get()
        if selected_patient == "No patient selected":
            messagebox.showwarning("Warning", "Please select a patient first!")
            return
        
        chief_complaint = self.quick_complaint_text.get("1.0", tk.END).strip()
        if not chief_complaint:
            messagebox.showerror("Error", "Chief complaint is required!")
            return
        
        try:
            patient_id = selected_patient.split(" - ")[0]
            
            visit_data = {
                "patient_id": patient_id,
                "visit_type": "OPD Consultation",
                "priority": self.quick_priority_var.get(),
                "status": "Waiting",
                "chief_complaint": chief_complaint
            }
            
            if self.opd_manager.add_visit(visit_data):
                messagebox.showinfo("Success", "Patient checked in successfully!")
                self.clear_checkin_selection()
                self.load_visits()
                self.refresh_queue()
            else:
                messagebox.showerror("Error", "Failed to check in patient!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error during check-in: {str(e)}")
    
    def load_visit_combo_data(self):
        """Load data for visit form combos"""
        try:
            # Load patients
            patients = self.patient_manager.get_all_patients()
            patient_options = [f"{p.get('id', '')} - {p.get('name', '')}" for p in patients]
            self.visit_patient_combo['values'] = patient_options
            
            # Load doctors
            doctors = self.doctor_manager.get_all_doctors()
            doctor_options = [f"{d.get('id', '')} - {d.get('name', '')}" for d in doctors]
            self.visit_doctor_combo['values'] = doctor_options
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading combo data: {str(e)}")
    
    def validate_visit_form(self):
        """Validate visit form"""
        # Check required fields
        if not self.visit_form_vars["patient_id"].get().strip():
            messagebox.showerror("Validation Error", "Patient is required!")
            return False
        
        chief_complaint = self.chief_complaint_text.get("1.0", tk.END).strip()
        if not chief_complaint:
            messagebox.showerror("Validation Error", "Chief complaint is required!")
            return False
        
        # Validate follow-up date if provided
        followup_date = self.visit_form_vars["followup_date"].get().strip()
        if followup_date:
            try:
                datetime.strptime(followup_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Invalid follow-up date format! Use YYYY-MM-DD")
                return False
        
        # Validate payment amount if provided
        payment_amount = self.visit_form_vars["payment_amount"].get().strip()
        if payment_amount:
            try:
                amount = float(payment_amount)
                if amount < 0:
                    messagebox.showerror("Validation Error", "Payment amount cannot be negative!")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Payment amount must be a valid number!")
                return False
        
        return True
    
    def get_visit_form_data(self):
        """Get data from visit form"""
        data = {}
        
        # Get combo selections
        for field_name, var in self.visit_form_vars.items():
            if field_name in ["patient_id", "doctor_id"]:
                value = var.get().strip()
                if value and " - " in value:
                    data[field_name] = value.split(" - ")[0]
                else:
                    data[field_name] = value
            else:
                data[field_name] = var.get().strip()
        
        # Get patient and doctor names
        patient_selection = self.visit_form_vars["patient_id"].get()
        if " - " in patient_selection:
            data["patient_name"] = patient_selection.split(" - ")[1]
        
        doctor_selection = self.visit_form_vars["doctor_id"].get()
        if " - " in doctor_selection:
            data["doctor_name"] = doctor_selection.split(" - ")[1]
        
        # Get text areas
        data["chief_complaint"] = self.chief_complaint_text.get("1.0", tk.END).strip()
        data["diagnosis"] = self.diagnosis_text.get("1.0", tk.END).strip()
        data["treatment"] = self.treatment_text.get("1.0", tk.END).strip()
        data["prescription"] = self.prescription_text.get("1.0", tk.END).strip()
        data["notes"] = self.visit_notes_text.get("1.0", tk.END).strip()
        
        return data
    
    def clear_visit_form(self):
        """Clear visit form"""
        for var in self.visit_form_vars.values():
            var.set("")
        
        # Clear text areas
        self.chief_complaint_text.delete("1.0", tk.END)
        self.diagnosis_text.delete("1.0", tk.END)
        self.treatment_text.delete("1.0", tk.END)
        self.prescription_text.delete("1.0", tk.END)
        self.visit_notes_text.delete("1.0", tk.END)
        
        self.current_visit_id = None
    
    def save_visit(self):
        """Save new visit"""
        if not self.validate_visit_form():
            return
        
        try:
            visit_data = self.get_visit_form_data()
            
            if self.opd_manager.add_visit(visit_data):
                messagebox.showinfo("Success", "Visit saved successfully!")
                self.clear_visit_form()
                self.load_visits()
                self.refresh_queue()
            else:
                messagebox.showerror("Error", "Failed to save visit!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving visit: {str(e)}")
    
    def update_visit(self):
        """Update existing visit"""
        if not self.current_visit_id:
            messagebox.showwarning("Warning", "No visit selected for update!")
            return
        
        if not self.validate_visit_form():
            return
        
        try:
            visit_data = self.get_visit_form_data()
            
            if self.opd_manager.update_visit(self.current_visit_id, visit_data):
                messagebox.showinfo("Success", "Visit updated successfully!")
                self.clear_visit_form()
                self.load_visits()
                self.refresh_queue()
            else:
                messagebox.showerror("Error", "Failed to update visit!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating visit: {str(e)}")
    
    def load_visits(self):
        """Load visits into list"""
        try:
            # Clear existing items
            for item in self.visit_tree.get_children():
                self.visit_tree.delete(item)
            
            # Load visits
            visits = self.opd_manager.get_all_visits()
            
            for visit in visits:
                self.visit_tree.insert("", tk.END, values=(
                    visit.get("id", ""),
                    visit.get("patient_name", visit.get("patient_id", "")),
                    visit.get("doctor_name", visit.get("doctor_id", "")),
                    visit.get("visit_date", ""),
                    visit.get("visit_time", ""),
                    visit.get("visit_type", ""),
                    visit.get("priority", ""),
                    visit.get("status", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading visits: {str(e)}")
    
    def on_visit_search(self, *args):
        """Handle visit search"""
        search_query = self.visit_search_var.get().strip().lower()
        
        try:
            # Clear existing items
            for item in self.visit_tree.get_children():
                self.visit_tree.delete(item)
            
            # Load and filter visits
            visits = self.opd_manager.get_all_visits()
            
            for visit in visits:
                # Search in patient name, doctor name, or visit ID
                if (not search_query or 
                    search_query in visit.get("patient_name", "").lower() or
                    search_query in visit.get("doctor_name", "").lower() or
                    search_query in visit.get("id", "").lower()):
                    
                    # Apply status filter
                    status_filter = self.visit_status_filter_var.get()
                    if status_filter == "All" or visit.get("status", "") == status_filter:
                        self.visit_tree.insert("", tk.END, values=(
                            visit.get("id", ""),
                            visit.get("patient_name", visit.get("patient_id", "")),
                            visit.get("doctor_name", visit.get("doctor_id", "")),
                            visit.get("visit_date", ""),
                            visit.get("visit_time", ""),
                            visit.get("visit_type", ""),
                            visit.get("priority", ""),
                            visit.get("status", "")
                        ))
                        
        except Exception as e:
            messagebox.showerror("Error", f"Error searching visits: {str(e)}")
    
    def on_visit_status_filter(self, event=None):
        """Handle visit status filter change"""
        self.on_visit_search()
    
    def filter_visits_by_date(self):
        """Filter visits by date"""
        filter_date = self.date_filter_var.get().strip()
        
        if not filter_date:
            messagebox.showwarning("Warning", "Please enter a date to filter!")
            return
        
        try:
            # Validate date format
            datetime.strptime(filter_date, "%Y-%m-%d")
            
            # Clear existing items
            for item in self.visit_tree.get_children():
                self.visit_tree.delete(item)
            
            # Load and filter visits
            visits = self.opd_manager.get_all_visits()
            
            for visit in visits:
                if visit.get("visit_date", "") == filter_date:
                    self.visit_tree.insert("", tk.END, values=(
                        visit.get("id", ""),
                        visit.get("patient_name", visit.get("patient_id", "")),
                        visit.get("doctor_name", visit.get("doctor_id", "")),
                        visit.get("visit_date", ""),
                        visit.get("visit_time", ""),
                        visit.get("visit_type", ""),
                        visit.get("priority", ""),
                        visit.get("status", "")
                    ))
                    
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering visits: {str(e)}")
    
    def show_todays_visits(self):
        """Show today's visits"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_filter_var.set(today)
        self.filter_visits_by_date()
    
    def on_visit_select(self, event):
        """Handle visit selection"""
        selection = self.visit_tree.selection()
        if selection:
            item = self.visit_tree.item(selection[0])
            visit_id = item['values'][0]
            self.edit_visit(visit_id)
    
    def edit_visit(self, visit_id):
        """Load visit data for editing"""
        try:
            visits = self.opd_manager.get_all_visits()
            visit = next((v for v in visits if v.get('id') == visit_id), None)
            
            if visit:
                self.current_visit_id = visit_id
                
                # Fill form with visit data
                self.visit_form_vars["patient_id"].set(f"{visit.get('patient_id', '')} - {visit.get('patient_name', '')}")
                self.visit_form_vars["doctor_id"].set(f"{visit.get('doctor_id', '')} - {visit.get('doctor_name', '')}")
                self.visit_form_vars["visit_type"].set(visit.get('visit_type', ''))
                self.visit_form_vars["priority"].set(visit.get('priority', ''))
                self.visit_form_vars["status"].set(visit.get('status', ''))
                self.visit_form_vars["followup_date"].set(visit.get('followup_date', ''))
                self.visit_form_vars["payment_amount"].set(visit.get('payment_amount', ''))
                
                # Fill text areas
                self.chief_complaint_text.delete("1.0", tk.END)
                self.chief_complaint_text.insert("1.0", visit.get('chief_complaint', ''))
                
                self.diagnosis_text.delete("1.0", tk.END)
                self.diagnosis_text.insert("1.0", visit.get('diagnosis', ''))
                
                self.treatment_text.delete("1.0", tk.END)
                self.treatment_text.insert("1.0", visit.get('treatment', ''))
                
                self.prescription_text.delete("1.0", tk.END)
                self.prescription_text.insert("1.0", visit.get('prescription', ''))
                
                self.visit_notes_text.delete("1.0", tk.END)
                self.visit_notes_text.insert("1.0", visit.get('notes', ''))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading visit data: {str(e)}")
    
    def edit_selected_visit(self):
        """Edit selected visit from list"""
        selection = self.visit_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a visit to edit!")
            return
        
        item = self.visit_tree.item(selection[0])
        visit_id = item['values'][0]
        self.edit_visit(visit_id)
    
    def mark_visit_complete(self):
        """Mark selected visit as complete"""
        selection = self.visit_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a visit to mark as complete!")
            return
        
        item = self.visit_tree.item(selection[0])
        visit_id = item['values'][0]
        
        try:
            if self.opd_manager.update_visit(visit_id, {"status": "Completed"}):
                messagebox.showinfo("Success", "Visit marked as completed!")
                self.load_visits()
                self.refresh_queue()
            else:
                messagebox.showerror("Error", "Failed to update visit status!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating visit: {str(e)}")
    
    def cancel_visit(self):
        """Cancel selected visit"""
        selection = self.visit_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a visit to cancel!")
            return
        
        item = self.visit_tree.item(selection[0])
        visit_id = item['values'][0]
        patient_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Cancel", 
                              f"Are you sure you want to cancel the visit for '{patient_name}'?"):
            try:
                if self.opd_manager.update_visit(visit_id, {"status": "Cancelled"}):
                    messagebox.showinfo("Success", "Visit cancelled successfully!")
                    self.load_visits()
                    self.refresh_queue()
                else:
                    messagebox.showerror("Error", "Failed to cancel visit!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error cancelling visit: {str(e)}")
    
    def delete_visit(self):
        """Delete selected visit"""
        selection = self.visit_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a visit to delete!")
            return
        
        item = self.visit_tree.item(selection[0])
        visit_id = item['values'][0]
        patient_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the visit for '{patient_name}'?\n\nThis action cannot be undone!"):
            try:
                visits = self.opd_manager.get_all_visits()
                visits = [v for v in visits if v.get('id') != visit_id]
                
                if self.opd_manager.file_io.save_data(self.opd_manager.filename, visits):
                    messagebox.showinfo("Success", "Visit deleted successfully!")
                    self.clear_visit_form()
                    self.load_visits()
                    self.refresh_queue()
                else:
                    messagebox.showerror("Error", "Failed to delete visit!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting visit: {str(e)}")
    
    def show_visit_context_menu(self, event):
        """Show context menu for visit list"""
        selection = self.visit_tree.selection()
        if not selection:
            return
        
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(label="Edit Visit", command=self.edit_selected_visit)
        context_menu.add_command(label="Mark Complete", command=self.mark_visit_complete)
        context_menu.add_command(label="Cancel Visit", command=self.cancel_visit)
        context_menu.add_separator()
        context_menu.add_command(label="Delete Visit", command=self.delete_visit)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def refresh_queue(self):
        """Refresh queue management"""
        try:
            visits = self.opd_manager.get_all_visits()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Count visits by status
            waiting_count = len([v for v in visits if v.get('status') == 'Waiting' and v.get('visit_date') == today])
            inprogress_count = len([v for v in visits if v.get('status') == 'In Progress' and v.get('visit_date') == today])
            completed_count = len([v for v in visits if v.get('status') == 'Completed' and v.get('visit_date') == today])
            
            self.waiting_count_var.set(str(waiting_count))
            self.inprogress_count_var.set(str(inprogress_count))
            self.completed_count_var.set(str(completed_count))
            
            # Load priority queue
            self.load_priority_queue()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing queue: {str(e)}")
    
    def load_priority_queue(self):
        """Load priority queue"""
        try:
            # Clear existing items
            for item in self.priority_tree.get_children():
                self.priority_tree.delete(item)
            
            # Get waiting visits for today
            visits = self.opd_manager.get_all_visits()
            today = datetime.now().strftime("%Y-%m-%d")
            waiting_visits = [v for v in visits if v.get('status') == 'Waiting' and v.get('visit_date') == today]
            
            # Sort by priority and time
            priority_order = {"Emergency": 1, "High": 2, "Normal": 3, "Low": 4}
            waiting_visits.sort(key=lambda x: (priority_order.get(x.get('priority', 'Normal'), 3), x.get('visit_time', '')))
            
            # Add to priority queue
            for position, visit in enumerate(waiting_visits, 1):
                # Calculate wait time
                visit_time = visit.get('visit_time', '')
                if visit_time:
                    try:
                        visit_datetime = datetime.strptime(f"{today} {visit_time}", "%Y-%m-%d %H:%M:%S")
                        wait_time = datetime.now() - visit_datetime
                        wait_minutes = int(wait_time.total_seconds() / 60)
                        wait_str = f"{wait_minutes} min"
                    except:
                        wait_str = "N/A"
                else:
                    wait_str = "N/A"
                
                self.priority_tree.insert("", tk.END, values=(
                    position,
                    visit.get("patient_name", visit.get("patient_id", "")),
                    visit.get("priority", ""),
                    visit.get("chief_complaint", "")[:50] + "..." if len(visit.get("chief_complaint", "")) > 50 else visit.get("chief_complaint", ""),
                    wait_str,
                    visit.get("id", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading priority queue: {str(e)}")
    
    def move_to_inprogress(self):
        """Move selected visit to in progress"""
        selection = self.priority_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a visit from the queue!")
            return
        
        item = self.priority_tree.item(selection[0])
        visit_id = item['values'][5]  # Action column contains visit ID
        
        try:
            if self.opd_manager.update_visit(visit_id, {"status": "In Progress"}):
                messagebox.showinfo("Success", "Visit moved to in progress!")
                self.load_visits()
                self.refresh_queue()
            else:
                messagebox.showerror("Error", "Failed to update visit status!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating visit: {str(e)}")
    
    def move_up_queue(self):
        """Move selected visit up in queue"""
        messagebox.showinfo("Info", "Queue reordering functionality would be implemented here.\nCurrently, queue is ordered by priority and time.")
    
    def move_down_queue(self):
        """Move selected visit down in queue"""
        messagebox.showinfo("Info", "Queue reordering functionality would be implemented here.\nCurrently, queue is ordered by priority and time.")
