"""
Patient Management Form for Hospital Management System
Handles patient registration, editing, and management operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

from utils.file_io import PatientManager
from utils.pdf_generator import PDFGenerator

class PatientForm:
    def __init__(self, parent, quick_mode=False):
        self.parent = parent
        self.patient_manager = PatientManager()
        self.pdf_generator = PDFGenerator()
        self.quick_mode = quick_mode
        self.current_patient_id = None
        
        self.create_window()
        self.setup_ui()
        self.load_patients()
    
    def create_window(self):
        """Create patient management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Patient Management")
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
        title_text = "Quick Patient Registration" if self.quick_mode else "Patient Management"
        ttk.Label(main_frame, text=title_text, font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create paned window for form and list
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Patient form
        self.create_patient_form(paned)
        
        # Right panel - Patient list
        if not self.quick_mode:
            self.create_patient_list(paned)
    
    def create_patient_form(self, parent):
        """Create patient registration/edit form"""
        form_frame = ttk.LabelFrame(parent, text="Patient Information", padding=20)
        parent.add(form_frame, weight=1)
        
        # Form fields
        fields = [
            ("Name*", "name"),
            ("Age*", "age"),
            ("Gender*", "gender"),
            ("Phone*", "phone"),
            ("Address", "address"),
            ("Emergency Contact", "emergency_contact"),
            ("Blood Group", "blood_group"),
            ("Medical History", "medical_history")
        ]
        
        self.form_vars = {}
        row = 0
        
        for label_text, field_name in fields:
            ttk.Label(form_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            if field_name == "gender":
                # Gender dropdown
                self.form_vars[field_name] = tk.StringVar()
                gender_combo = ttk.Combobox(form_frame, textvariable=self.form_vars[field_name],
                                          values=["Male", "Female", "Other"], state="readonly", width=30)
                gender_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
            elif field_name in ["medical_history", "address"]:
                # Text area for longer text
                self.form_vars[field_name] = tk.StringVar()
                text_widget = tk.Text(form_frame, height=3, width=32)
                text_widget.grid(row=row, column=1, sticky=tk.W, pady=5)
                self.form_vars[f"{field_name}_widget"] = text_widget
            else:
                # Regular entry
                self.form_vars[field_name] = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=self.form_vars[field_name], width=32)
                entry.grid(row=row, column=1, sticky=tk.W, pady=5)
            
            row += 1
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Action buttons
        ttk.Button(buttons_frame, text="Add Patient", 
                  command=self.add_patient).pack(side=tk.LEFT, padx=5)
        
        if not self.quick_mode:
            ttk.Button(buttons_frame, text="Update Patient", 
                      command=self.update_patient).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Clear Form", 
                      command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_patient_list(self, parent):
        """Create patient list with search functionality"""
        list_frame = ttk.LabelFrame(parent, text="Patient List", padding=10)
        parent.add(list_frame, weight=2)
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(search_frame, text="Clear Search", 
                  command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Patient list
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for patient list
        columns = ("ID", "Name", "Age", "Gender", "Phone", "Registration Date")
        self.patient_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.patient_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.patient_tree.xview)
        self.patient_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.patient_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.patient_tree.bind("<Double-1>", self.on_patient_select)
        self.patient_tree.bind("<Button-3>", self.show_patient_context_menu)
        
        # Action buttons for patient list
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Edit Selected", 
                  command=self.edit_selected_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_selected_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Generate PDF", 
                  command=self.generate_patient_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh List", 
                  command=self.load_patients).pack(side=tk.LEFT, padx=5)
    
    def validate_form(self):
        """Validate form data"""
        required_fields = ["name", "age", "gender", "phone"]
        
        for field in required_fields:
            if field in self.form_vars:
                value = self.form_vars[field].get().strip()
                if not value:
                    messagebox.showerror("Validation Error", f"{field.title()} is required!")
                    return False
        
        # Validate age
        try:
            age = int(self.form_vars["age"].get().strip())
            if age < 0 or age > 150:
                messagebox.showerror("Validation Error", "Age must be between 0 and 150!")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Age must be a valid number!")
            return False
        
        # Validate phone
        phone = self.form_vars["phone"].get().strip()
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            messagebox.showerror("Validation Error", "Phone number contains invalid characters!")
            return False
        
        return True
    
    def get_form_data(self):
        """Get data from form fields"""
        data = {}
        
        for field_name, var in self.form_vars.items():
            if field_name.endswith("_widget"):
                # Handle text widgets
                widget = var
                content = widget.get("1.0", tk.END).strip()
                field_name = field_name.replace("_widget", "")
                data[field_name] = content
            elif isinstance(var, tk.StringVar):
                data[field_name] = var.get().strip()
        
        return data
    
    def clear_form(self):
        """Clear all form fields"""
        for field_name, var in self.form_vars.items():
            if field_name.endswith("_widget"):
                # Handle text widgets
                widget = var
                widget.delete("1.0", tk.END)
            elif isinstance(var, tk.StringVar):
                var.set("")
        
        self.current_patient_id = None
    
    def add_patient(self):
        """Add new patient"""
        if not self.validate_form():
            return
        
        try:
            patient_data = self.get_form_data()
            
            if self.patient_manager.add_patient(patient_data):
                messagebox.showinfo("Success", "Patient added successfully!")
                self.clear_form()
                if not self.quick_mode:
                    self.load_patients()
                else:
                    self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add patient!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error adding patient: {str(e)}")
    
    def update_patient(self):
        """Update existing patient"""
        if not self.current_patient_id:
            messagebox.showwarning("Warning", "No patient selected for update!")
            return
        
        if not self.validate_form():
            return
        
        try:
            patient_data = self.get_form_data()
            
            if self.patient_manager.update_patient(self.current_patient_id, patient_data):
                messagebox.showinfo("Success", "Patient updated successfully!")
                self.clear_form()
                self.load_patients()
            else:
                messagebox.showerror("Error", "Failed to update patient!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating patient: {str(e)}")
    
    def load_patients(self):
        """Load patients into the list"""
        if self.quick_mode:
            return
        
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
                    patient.get("gender", ""),
                    patient.get("phone", ""),
                    patient.get("registration_date", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patients: {str(e)}")
    
    def on_search(self, *args):
        """Handle search functionality"""
        if self.quick_mode:
            return
        
        search_query = self.search_var.get().strip()
        
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
                    patient.get("gender", ""),
                    patient.get("phone", ""),
                    patient.get("registration_date", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching patients: {str(e)}")
    
    def clear_search(self):
        """Clear search and reload all patients"""
        self.search_var.set("")
    
    def on_patient_select(self, event):
        """Handle patient selection"""
        selection = self.patient_tree.selection()
        if selection:
            item = self.patient_tree.item(selection[0])
            patient_id = item['values'][0]
            self.edit_patient(patient_id)
    
    def edit_patient(self, patient_id):
        """Load patient data into form for editing"""
        try:
            patient = self.patient_manager.get_patient_by_id(patient_id)
            if patient:
                self.current_patient_id = patient_id
                
                # Fill form with patient data
                for field_name, var in self.form_vars.items():
                    if field_name.endswith("_widget"):
                        # Handle text widgets
                        widget = var
                        field_name = field_name.replace("_widget", "")
                        widget.delete("1.0", tk.END)
                        widget.insert("1.0", patient.get(field_name, ""))
                    elif isinstance(var, tk.StringVar):
                        var.set(patient.get(field_name, ""))
                        
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patient data: {str(e)}")
    
    def edit_selected_patient(self):
        """Edit selected patient from list"""
        selection = self.patient_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient to edit!")
            return
        
        item = self.patient_tree.item(selection[0])
        patient_id = item['values'][0]
        self.edit_patient(patient_id)
    
    def delete_selected_patient(self):
        """Delete selected patient"""
        selection = self.patient_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient to delete!")
            return
        
        item = self.patient_tree.item(selection[0])
        patient_id = item['values'][0]
        patient_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete patient '{patient_name}' (ID: {patient_id})?\n\nThis action cannot be undone!"):
            try:
                if self.patient_manager.delete_patient(patient_id):
                    messagebox.showinfo("Success", "Patient deleted successfully!")
                    self.clear_form()
                    self.load_patients()
                else:
                    messagebox.showerror("Error", "Failed to delete patient!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting patient: {str(e)}")
    
    def generate_patient_pdf(self):
        """Generate PDF for selected patient"""
        selection = self.patient_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient to generate PDF!")
            return
        
        item = self.patient_tree.item(selection[0])
        patient_id = item['values'][0]
        
        try:
            filepath = self.pdf_generator.generate_patient_summary(patient_id)
            messagebox.showinfo("Success", f"Patient PDF generated successfully!\n\nFile: {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF: {str(e)}")
    
    def show_patient_context_menu(self, event):
        """Show context menu for patient list"""
        selection = self.patient_tree.selection()
        if not selection:
            return
        
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(label="Edit Patient", command=self.edit_selected_patient)
        context_menu.add_command(label="Delete Patient", command=self.delete_selected_patient)
        context_menu.add_separator()
        context_menu.add_command(label="Generate PDF", command=self.generate_patient_pdf)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
