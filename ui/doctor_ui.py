"""
Doctor Management UI for Hospital Management System
Handles doctor registration, scheduling, and availability management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time
import re

from utils.file_io import DoctorManager

class DoctorUI:
    def __init__(self, parent):
        self.parent = parent
        self.doctor_manager = DoctorManager()
        self.current_doctor_id = None
        
        self.create_window()
        self.setup_ui()
        self.load_doctors()
    
    def create_window(self):
        """Create doctor management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Doctor Management")
        self.window.geometry("1000x700")
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
        ttk.Label(main_frame, text="Doctor Management", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Doctor registration tab
        self.create_doctor_form_tab(notebook)
        
        # Doctor list tab
        self.create_doctor_list_tab(notebook)
        
        # Doctor schedule tab
        self.create_schedule_tab(notebook)
    
    def create_doctor_form_tab(self, notebook):
        """Create doctor registration form tab"""
        form_frame = ttk.Frame(notebook)
        notebook.add(form_frame, text="Add/Edit Doctor")
        
        # Form container
        form_container = ttk.LabelFrame(form_frame, text="Doctor Information", padding=20)
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Form fields
        self.form_vars = {}
        row = 0
        
        fields = [
            ("Name*", "name"),
            ("Specialization*", "specialization"),
            ("Qualification", "qualification"),
            ("Experience (Years)", "experience"),
            ("Phone*", "phone"),
            ("Email", "email"),
            ("License Number", "license_number"),
            ("Department", "department"),
            ("Consultation Fee", "consultation_fee")
        ]
        
        for label_text, field_name in fields:
            ttk.Label(form_container, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            if field_name == "specialization":
                # Specialization dropdown
                self.form_vars[field_name] = tk.StringVar()
                spec_combo = ttk.Combobox(form_container, textvariable=self.form_vars[field_name],
                                        values=["General Medicine", "Cardiology", "Dermatology", "Orthopedics", 
                                               "Pediatrics", "Gynecology", "Neurology", "Psychiatry", "Surgery",
                                               "Radiology", "Pathology", "Anesthesiology", "Emergency Medicine"],
                                        width=40)
                spec_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
            elif field_name == "department":
                # Department dropdown
                self.form_vars[field_name] = tk.StringVar()
                dept_combo = ttk.Combobox(form_container, textvariable=self.form_vars[field_name],
                                        values=["OPD", "Emergency", "ICU", "Surgery", "Maternity", "Pediatrics",
                                               "Cardiology", "Neurology", "Orthopedics", "Radiology"],
                                        width=40)
                dept_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
            else:
                # Regular entry
                self.form_vars[field_name] = tk.StringVar()
                entry = ttk.Entry(form_container, textvariable=self.form_vars[field_name], width=42)
                entry.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
            
            row += 1
        
        # Address field (text area)
        ttk.Label(form_container, text="Address").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.address_text = tk.Text(form_container, height=3, width=50)
        self.address_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Notes field (text area)
        ttk.Label(form_container, text="Notes").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.notes_text = tk.Text(form_container, height=3, width=50)
        self.notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(form_container)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="Add Doctor", 
                  command=self.add_doctor).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Update Doctor", 
                  command=self.update_doctor).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear Form", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_doctor_list_tab(self, notebook):
        """Create doctor list tab"""
        list_frame = ttk.Frame(notebook)
        notebook.add(list_frame, text="Doctor List")
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Department Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.dept_filter_var = tk.StringVar(value="All")
        dept_filter = ttk.Combobox(search_frame, textvariable=self.dept_filter_var,
                                 values=["All", "OPD", "Emergency", "ICU", "Surgery", "Maternity", 
                                        "Pediatrics", "Cardiology", "Neurology", "Orthopedics", "Radiology"],
                                 width=15, state="readonly")
        dept_filter.pack(side=tk.LEFT, padx=5)
        dept_filter.bind("<<ComboboxSelected>>", self.on_department_filter)
        
        ttk.Button(search_frame, text="Refresh", 
                  command=self.load_doctors).pack(side=tk.LEFT, padx=20)
        
        # Doctor list
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Specialization", "Department", "Phone", "Experience", "Consultation Fee")
        self.doctor_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.doctor_tree.heading(col, text=col)
            if col == "ID":
                self.doctor_tree.column(col, width=80)
            elif col == "Name":
                self.doctor_tree.column(col, width=150)
            elif col == "Specialization":
                self.doctor_tree.column(col, width=120)
            elif col == "Phone":
                self.doctor_tree.column(col, width=120)
            else:
                self.doctor_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.doctor_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.doctor_tree.xview)
        self.doctor_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.doctor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.doctor_tree.bind("<Double-1>", self.on_doctor_select)
        self.doctor_tree.bind("<Button-3>", self.show_context_menu)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(action_frame, text="Edit Selected", 
                  command=self.edit_selected_doctor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_selected_doctor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="View Details", 
                  command=self.view_doctor_details).pack(side=tk.LEFT, padx=5)
    
    def create_schedule_tab(self, notebook):
        """Create doctor schedule management tab"""
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Doctor Schedule")
        
        # Doctor selection
        selection_frame = ttk.Frame(schedule_frame)
        selection_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(selection_frame, text="Select Doctor:").pack(side=tk.LEFT, padx=5)
        self.schedule_doctor_var = tk.StringVar()
        self.schedule_doctor_combo = ttk.Combobox(selection_frame, textvariable=self.schedule_doctor_var,
                                                width=40, state="readonly")
        self.schedule_doctor_combo.pack(side=tk.LEFT, padx=5)
        self.schedule_doctor_combo.bind("<<ComboboxSelected>>", self.on_schedule_doctor_select)
        
        ttk.Button(selection_frame, text="Load Schedule", 
                  command=self.load_doctor_schedule).pack(side=tk.LEFT, padx=20)
        
        # Schedule container
        schedule_container = ttk.LabelFrame(schedule_frame, text="Weekly Schedule", padding=10)
        schedule_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Days of week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Schedule grid
        self.schedule_vars = {}
        row = 0
        
        # Headers
        ttk.Label(schedule_container, text="Day", font=('Arial', 10, 'bold')).grid(row=row, column=0, padx=5, pady=5)
        ttk.Label(schedule_container, text="Available", font=('Arial', 10, 'bold')).grid(row=row, column=1, padx=5, pady=5)
        ttk.Label(schedule_container, text="Start Time", font=('Arial', 10, 'bold')).grid(row=row, column=2, padx=5, pady=5)
        ttk.Label(schedule_container, text="End Time", font=('Arial', 10, 'bold')).grid(row=row, column=3, padx=5, pady=5)
        ttk.Label(schedule_container, text="Break Start", font=('Arial', 10, 'bold')).grid(row=row, column=4, padx=5, pady=5)
        ttk.Label(schedule_container, text="Break End", font=('Arial', 10, 'bold')).grid(row=row, column=5, padx=5, pady=5)
        row += 1
        
        # Time slots
        time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(6, 24) for minute in [0, 30]]
        
        for day in days:
            ttk.Label(schedule_container, text=day).grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
            
            # Available checkbox
            available_var = tk.BooleanVar()
            ttk.Checkbutton(schedule_container, variable=available_var).grid(row=row, column=1, padx=5, pady=2)
            
            # Start time
            start_var = tk.StringVar(value="09:00")
            start_combo = ttk.Combobox(schedule_container, textvariable=start_var, values=time_slots, width=10)
            start_combo.grid(row=row, column=2, padx=5, pady=2)
            
            # End time
            end_var = tk.StringVar(value="17:00")
            end_combo = ttk.Combobox(schedule_container, textvariable=end_var, values=time_slots, width=10)
            end_combo.grid(row=row, column=3, padx=5, pady=2)
            
            # Break start
            break_start_var = tk.StringVar(value="12:00")
            break_start_combo = ttk.Combobox(schedule_container, textvariable=break_start_var, values=time_slots, width=10)
            break_start_combo.grid(row=row, column=4, padx=5, pady=2)
            
            # Break end
            break_end_var = tk.StringVar(value="13:00")
            break_end_combo = ttk.Combobox(schedule_container, textvariable=break_end_var, values=time_slots, width=10)
            break_end_combo.grid(row=row, column=5, padx=5, pady=2)
            
            self.schedule_vars[day] = {
                'available': available_var,
                'start_time': start_var,
                'end_time': end_var,
                'break_start': break_start_var,
                'break_end': break_end_var
            }
            
            row += 1
        
        # Schedule buttons
        schedule_buttons_frame = ttk.Frame(schedule_container)
        schedule_buttons_frame.grid(row=row, column=0, columnspan=6, pady=20)
        
        ttk.Button(schedule_buttons_frame, text="Save Schedule", 
                  command=self.save_doctor_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(schedule_buttons_frame, text="Clear Schedule", 
                  command=self.clear_schedule).pack(side=tk.LEFT, padx=5)
        
        # Load doctor combo data
        self.load_schedule_combo_data()
    
    def validate_form(self):
        """Validate doctor form"""
        required_fields = ["name", "specialization", "phone"]
        
        for field in required_fields:
            if not self.form_vars[field].get().strip():
                messagebox.showerror("Validation Error", f"{field.title()} is required!")
                return False
        
        # Validate phone
        phone = self.form_vars["phone"].get().strip()
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            messagebox.showerror("Validation Error", "Phone number contains invalid characters!")
            return False
        
        # Validate email if provided
        email = self.form_vars.get("email", tk.StringVar()).get().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Validation Error", "Invalid email format!")
            return False
        
        # Validate experience if provided
        experience = self.form_vars.get("experience", tk.StringVar()).get().strip()
        if experience:
            try:
                exp_val = float(experience)
                if exp_val < 0 or exp_val > 60:
                    messagebox.showerror("Validation Error", "Experience must be between 0 and 60 years!")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Experience must be a valid number!")
                return False
        
        # Validate consultation fee if provided
        fee = self.form_vars.get("consultation_fee", tk.StringVar()).get().strip()
        if fee:
            try:
                fee_val = float(fee)
                if fee_val < 0:
                    messagebox.showerror("Validation Error", "Consultation fee cannot be negative!")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Consultation fee must be a valid number!")
                return False
        
        return True
    
    def get_form_data(self):
        """Get data from form"""
        data = {}
        
        for field_name, var in self.form_vars.items():
            data[field_name] = var.get().strip()
        
        # Get text areas
        data["address"] = self.address_text.get("1.0", tk.END).strip()
        data["notes"] = self.notes_text.get("1.0", tk.END).strip()
        
        return data
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            var.set("")
        
        self.address_text.delete("1.0", tk.END)
        self.notes_text.delete("1.0", tk.END)
        self.current_doctor_id = None
    
    def add_doctor(self):
        """Add new doctor"""
        if not self.validate_form():
            return
        
        try:
            doctor_data = self.get_form_data()
            
            if self.doctor_manager.add_doctor(doctor_data):
                messagebox.showinfo("Success", "Doctor added successfully!")
                self.clear_form()
                self.load_doctors()
                self.load_schedule_combo_data()
            else:
                messagebox.showerror("Error", "Failed to add doctor!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error adding doctor: {str(e)}")
    
    def update_doctor(self):
        """Update existing doctor"""
        if not self.current_doctor_id:
            messagebox.showwarning("Warning", "No doctor selected for update!")
            return
        
        if not self.validate_form():
            return
        
        try:
            doctor_data = self.get_form_data()
            
            if self.doctor_manager.update_doctor(self.current_doctor_id, doctor_data):
                messagebox.showinfo("Success", "Doctor updated successfully!")
                self.clear_form()
                self.load_doctors()
                self.load_schedule_combo_data()
            else:
                messagebox.showerror("Error", "Failed to update doctor!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating doctor: {str(e)}")
    
    def load_doctors(self):
        """Load doctors into the list"""
        try:
            # Clear existing items
            for item in self.doctor_tree.get_children():
                self.doctor_tree.delete(item)
            
            # Load doctors
            doctors = self.doctor_manager.get_all_doctors()
            
            for doctor in doctors:
                self.doctor_tree.insert("", tk.END, values=(
                    doctor.get("id", ""),
                    doctor.get("name", ""),
                    doctor.get("specialization", ""),
                    doctor.get("department", ""),
                    doctor.get("phone", ""),
                    doctor.get("experience", ""),
                    doctor.get("consultation_fee", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading doctors: {str(e)}")
    
    def on_search(self, *args):
        """Handle search functionality"""
        search_query = self.search_var.get().strip().lower()
        
        try:
            # Clear existing items
            for item in self.doctor_tree.get_children():
                self.doctor_tree.delete(item)
            
            # Load and filter doctors
            doctors = self.doctor_manager.get_all_doctors()
            
            for doctor in doctors:
                # Search in name, specialization, or ID
                if (not search_query or 
                    search_query in doctor.get("name", "").lower() or
                    search_query in doctor.get("specialization", "").lower() or
                    search_query in doctor.get("id", "").lower()):
                    
                    # Apply department filter
                    dept_filter = self.dept_filter_var.get()
                    if dept_filter == "All" or doctor.get("department", "") == dept_filter:
                        self.doctor_tree.insert("", tk.END, values=(
                            doctor.get("id", ""),
                            doctor.get("name", ""),
                            doctor.get("specialization", ""),
                            doctor.get("department", ""),
                            doctor.get("phone", ""),
                            doctor.get("experience", ""),
                            doctor.get("consultation_fee", "")
                        ))
                        
        except Exception as e:
            messagebox.showerror("Error", f"Error searching doctors: {str(e)}")
    
    def on_department_filter(self, event=None):
        """Handle department filter change"""
        self.on_search()
    
    def on_doctor_select(self, event):
        """Handle doctor selection"""
        selection = self.doctor_tree.selection()
        if selection:
            item = self.doctor_tree.item(selection[0])
            doctor_id = item['values'][0]
            self.edit_doctor(doctor_id)
    
    def edit_doctor(self, doctor_id):
        """Load doctor data for editing"""
        try:
            doctors = self.doctor_manager.get_all_doctors()
            doctor = next((d for d in doctors if d.get('id') == doctor_id), None)
            
            if doctor:
                self.current_doctor_id = doctor_id
                
                # Fill form with doctor data
                for field_name, var in self.form_vars.items():
                    var.set(doctor.get(field_name, ""))
                
                # Fill text areas
                self.address_text.delete("1.0", tk.END)
                self.address_text.insert("1.0", doctor.get("address", ""))
                
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", doctor.get("notes", ""))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading doctor data: {str(e)}")
    
    def edit_selected_doctor(self):
        """Edit selected doctor from list"""
        selection = self.doctor_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a doctor to edit!")
            return
        
        item = self.doctor_tree.item(selection[0])
        doctor_id = item['values'][0]
        self.edit_doctor(doctor_id)
    
    def delete_selected_doctor(self):
        """Delete selected doctor"""
        selection = self.doctor_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a doctor to delete!")
            return
        
        item = self.doctor_tree.item(selection[0])
        doctor_id = item['values'][0]
        doctor_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete Dr. '{doctor_name}' (ID: {doctor_id})?\n\nThis action cannot be undone!"):
            try:
                if self.doctor_manager.delete_doctor(doctor_id):
                    messagebox.showinfo("Success", "Doctor deleted successfully!")
                    self.clear_form()
                    self.load_doctors()
                    self.load_schedule_combo_data()
                else:
                    messagebox.showerror("Error", "Failed to delete doctor!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting doctor: {str(e)}")
    
    def view_doctor_details(self):
        """View detailed doctor information"""
        selection = self.doctor_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a doctor to view details!")
            return
        
        item = self.doctor_tree.item(selection[0])
        doctor_id = item['values'][0]
        
        try:
            doctors = self.doctor_manager.get_all_doctors()
            doctor = next((d for d in doctors if d.get('id') == doctor_id), None)
            
            if doctor:
                self.show_doctor_details_window(doctor)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading doctor details: {str(e)}")
    
    def show_doctor_details_window(self, doctor):
        """Show doctor details in a separate window"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Doctor Details - {doctor.get('name', 'Unknown')}")
        details_window.geometry("500x600")
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
        
        # Doctor details
        details_frame = ttk.LabelFrame(scrollable_frame, text="Doctor Information", padding=20)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Display doctor information
        fields = [
            ("ID", "id"),
            ("Name", "name"),
            ("Specialization", "specialization"),
            ("Qualification", "qualification"),
            ("Experience", "experience"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("License Number", "license_number"),
            ("Department", "department"),
            ("Consultation Fee", "consultation_fee"),
            ("Address", "address"),
            ("Notes", "notes")
        ]
        
        row = 0
        for label_text, field_name in fields:
            ttk.Label(details_frame, text=f"{label_text}:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(details_frame, text=doctor.get(field_name, "N/A"), wraplength=300).grid(row=row, column=1, sticky=tk.W, pady=5)
            row += 1
        
        # Close button
        ttk.Button(details_frame, text="Close", command=details_window.destroy).grid(row=row, column=0, columnspan=2, pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_context_menu(self, event):
        """Show context menu for doctor list"""
        selection = self.doctor_tree.selection()
        if not selection:
            return
        
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(label="Edit Doctor", command=self.edit_selected_doctor)
        context_menu.add_command(label="Delete Doctor", command=self.delete_selected_doctor)
        context_menu.add_separator()
        context_menu.add_command(label="View Details", command=self.view_doctor_details)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def load_schedule_combo_data(self):
        """Load doctors for schedule combo"""
        try:
            doctors = self.doctor_manager.get_all_doctors()
            doctor_options = [f"{d.get('id', '')} - {d.get('name', '')}" for d in doctors]
            self.schedule_doctor_combo['values'] = doctor_options
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading schedule combo data: {str(e)}")
    
    def on_schedule_doctor_select(self, event=None):
        """Handle doctor selection for schedule"""
        self.load_doctor_schedule()
    
    def load_doctor_schedule(self):
        """Load doctor schedule"""
        doctor_selection = self.schedule_doctor_var.get()
        if not doctor_selection:
            return
        
        try:
            doctor_id = doctor_selection.split(" - ")[0]
            doctors = self.doctor_manager.get_all_doctors()
            doctor = next((d for d in doctors if d.get('id') == doctor_id), None)
            
            if doctor and 'schedule' in doctor:
                schedule = doctor['schedule']
                for day, day_schedule in schedule.items():
                    if day in self.schedule_vars:
                        self.schedule_vars[day]['available'].set(day_schedule.get('available', False))
                        self.schedule_vars[day]['start_time'].set(day_schedule.get('start_time', '09:00'))
                        self.schedule_vars[day]['end_time'].set(day_schedule.get('end_time', '17:00'))
                        self.schedule_vars[day]['break_start'].set(day_schedule.get('break_start', '12:00'))
                        self.schedule_vars[day]['break_end'].set(day_schedule.get('break_end', '13:00'))
            else:
                self.clear_schedule()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading doctor schedule: {str(e)}")
    
    def save_doctor_schedule(self):
        """Save doctor schedule"""
        doctor_selection = self.schedule_doctor_var.get()
        if not doctor_selection:
            messagebox.showwarning("Warning", "Please select a doctor first!")
            return
        
        try:
            doctor_id = doctor_selection.split(" - ")[0]
            
            # Get schedule data
            schedule = {}
            for day, vars_dict in self.schedule_vars.items():
                schedule[day] = {
                    'available': vars_dict['available'].get(),
                    'start_time': vars_dict['start_time'].get(),
                    'end_time': vars_dict['end_time'].get(),
                    'break_start': vars_dict['break_start'].get(),
                    'break_end': vars_dict['break_end'].get()
                }
            
            # Update doctor with schedule
            if self.doctor_manager.update_doctor(doctor_id, {'schedule': schedule}):
                messagebox.showinfo("Success", "Doctor schedule saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save doctor schedule!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving doctor schedule: {str(e)}")
    
    def clear_schedule(self):
        """Clear schedule form"""
        for day_vars in self.schedule_vars.values():
            day_vars['available'].set(False)
            day_vars['start_time'].set("09:00")
            day_vars['end_time'].set("17:00")
            day_vars['break_start'].set("12:00")
            day_vars['break_end'].set("13:00")
