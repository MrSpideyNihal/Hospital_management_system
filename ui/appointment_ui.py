"""
Appointment Management UI for Hospital Management System
Handles appointment scheduling, calendar view, and appointment management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar

from utils.file_io import AppointmentManager, PatientManager, DoctorManager

class AppointmentUI:
    def __init__(self, parent, quick_mode=False):
        self.parent = parent
        self.appointment_manager = AppointmentManager()
        self.patient_manager = PatientManager()
        self.doctor_manager = DoctorManager()
        self.quick_mode = quick_mode
        self.current_appointment_id = None
        self.current_date = datetime.now()
        
        self.create_window()
        self.setup_ui()
        self.load_appointments()
        self.load_calendar()
    
    def create_window(self):
        """Create appointment management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Appointment Management")
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
        title_text = "Quick Appointment Booking" if self.quick_mode else "Appointment Management"
        ttk.Label(main_frame, text=title_text, font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Appointment form tab
        self.create_appointment_form_tab(notebook)
        
        # Calendar view tab
        if not self.quick_mode:
            self.create_calendar_tab(notebook)
            
            # Appointment list tab
            self.create_appointment_list_tab(notebook)
    
    def create_appointment_form_tab(self, notebook):
        """Create appointment booking form tab"""
        form_frame = ttk.Frame(notebook)
        notebook.add(form_frame, text="Book Appointment")
        
        # Form container
        form_container = ttk.LabelFrame(form_frame, text="Appointment Details", padding=20)
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Form fields
        self.form_vars = {}
        row = 0
        
        # Patient selection
        ttk.Label(form_container, text="Patient*").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.form_vars["patient_id"] = tk.StringVar()
        patient_combo = ttk.Combobox(form_container, textvariable=self.form_vars["patient_id"], 
                                   width=40, state="readonly")
        patient_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        self.patient_combo = patient_combo
        row += 1
        
        # Doctor selection
        ttk.Label(form_container, text="Doctor*").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.form_vars["doctor_id"] = tk.StringVar()
        doctor_combo = ttk.Combobox(form_container, textvariable=self.form_vars["doctor_id"], 
                                  width=40, state="readonly")
        doctor_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        self.doctor_combo = doctor_combo
        row += 1
        
        # Appointment date
        ttk.Label(form_container, text="Date*").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.form_vars["appointment_date"] = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form_container, textvariable=self.form_vars["appointment_date"], width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(form_container, text="(YYYY-MM-DD)").grid(row=row, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Appointment time
        ttk.Label(form_container, text="Time*").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.form_vars["appointment_time"] = tk.StringVar()
        time_combo = ttk.Combobox(form_container, textvariable=self.form_vars["appointment_time"], 
                                width=20, values=self.generate_time_slots())
        time_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Appointment type
        ttk.Label(form_container, text="Type").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.form_vars["appointment_type"] = tk.StringVar()
        type_combo = ttk.Combobox(form_container, textvariable=self.form_vars["appointment_type"], 
                                width=40, values=["Consultation", "Follow-up", "Check-up", "Emergency", "Surgery"])
        type_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Status
        ttk.Label(form_container, text="Status").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.form_vars["status"] = tk.StringVar(value="Scheduled")
        status_combo = ttk.Combobox(form_container, textvariable=self.form_vars["status"], 
                                  width=40, values=["Scheduled", "Confirmed", "In Progress", "Completed", "Cancelled"])
        status_combo.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Notes
        ttk.Label(form_container, text="Notes").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.notes_text = tk.Text(form_container, height=4, width=50)
        self.notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, columnspan=2)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(form_container)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="Book Appointment", 
                  command=self.book_appointment).pack(side=tk.LEFT, padx=5)
        
        if not self.quick_mode:
            ttk.Button(buttons_frame, text="Update Appointment", 
                      command=self.update_appointment).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Clear Form", 
                      command=self.clear_appointment_form).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Load combo box data
        self.load_combo_data()
    
    def create_calendar_tab(self, notebook):
        """Create calendar view tab"""
        calendar_frame = ttk.Frame(notebook)
        notebook.add(calendar_frame, text="Calendar View")
        
        # Calendar controls
        controls_frame = ttk.Frame(calendar_frame)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(controls_frame, text="Previous Month", 
                  command=self.previous_month).pack(side=tk.LEFT, padx=5)
        
        self.calendar_label = ttk.Label(controls_frame, text="", font=('Arial', 14, 'bold'))
        self.calendar_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(controls_frame, text="Next Month", 
                  command=self.next_month).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Today", 
                  command=self.go_to_today).pack(side=tk.LEFT, padx=20)
        
        # Calendar display
        calendar_container = ttk.Frame(calendar_frame)
        calendar_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create calendar grid
        self.calendar_buttons = {}
        self.calendar_grid = ttk.Frame(calendar_container)
        self.calendar_grid.pack()
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(self.calendar_grid, text=day, font=('Arial', 10, 'bold')).grid(row=0, column=i, padx=1, pady=1)
        
        # Create calendar buttons
        for week in range(6):
            for day in range(7):
                btn = tk.Button(self.calendar_grid, text="", width=8, height=3,
                              command=lambda w=week, d=day: self.on_calendar_day_click(w, d))
                btn.grid(row=week+1, column=day, padx=1, pady=1)
                self.calendar_buttons[(week, day)] = btn
        
        # Selected date appointments
        self.selected_date_frame = ttk.LabelFrame(calendar_frame, text="Appointments for Selected Date", padding=10)
        self.selected_date_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.selected_date_tree = ttk.Treeview(self.selected_date_frame, 
                                             columns=("Time", "Patient", "Doctor", "Type", "Status"), 
                                             show="headings", height=6)
        
        for col in ["Time", "Patient", "Doctor", "Type", "Status"]:
            self.selected_date_tree.heading(col, text=col)
            self.selected_date_tree.column(col, width=120)
        
        self.selected_date_tree.pack(fill=tk.X)
    
    def create_appointment_list_tab(self, notebook):
        """Create appointment list tab"""
        list_frame = ttk.Frame(notebook)
        notebook.add(list_frame, text="Appointment List")
        
        # Search and filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_appointment_search)
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Status Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.status_filter_var = tk.StringVar(value="All")
        status_filter = ttk.Combobox(filter_frame, textvariable=self.status_filter_var, 
                                   values=["All", "Scheduled", "Confirmed", "In Progress", "Completed", "Cancelled"],
                                   width=15, state="readonly")
        status_filter.pack(side=tk.LEFT, padx=5)
        status_filter.bind("<<ComboboxSelected>>", self.on_status_filter)
        
        ttk.Button(filter_frame, text="Refresh", 
                  command=self.load_appointments).pack(side=tk.LEFT, padx=20)
        
        # Appointments list
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Patient", "Doctor", "Date", "Time", "Type", "Status")
        self.appointment_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.appointment_tree.heading(col, text=col)
            self.appointment_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.appointment_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.appointment_tree.xview)
        self.appointment_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.appointment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.appointment_tree.bind("<Double-1>", self.on_appointment_select)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(action_frame, text="Edit Selected", 
                  command=self.edit_selected_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_selected_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Mark Complete", 
                  command=self.mark_appointment_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel Appointment", 
                  command=self.cancel_appointment).pack(side=tk.LEFT, padx=5)
    
    def generate_time_slots(self):
        """Generate available time slots"""
        slots = []
        for hour in range(9, 18):  # 9 AM to 6 PM
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                slots.append(time_str)
        return slots
    
    def load_combo_data(self):
        """Load data for combo boxes"""
        try:
            # Load patients
            patients = self.patient_manager.get_all_patients()
            patient_options = [f"{p.get('id', '')} - {p.get('name', '')}" for p in patients]
            self.patient_combo['values'] = patient_options
            
            # Load doctors
            doctors = self.doctor_manager.get_all_doctors()
            doctor_options = [f"{d.get('id', '')} - {d.get('name', '')}" for d in doctors]
            self.doctor_combo['values'] = doctor_options
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading combo data: {str(e)}")
    
    def validate_appointment_form(self):
        """Validate appointment form"""
        required_fields = ["patient_id", "doctor_id", "appointment_date", "appointment_time"]
        
        for field in required_fields:
            if not self.form_vars[field].get().strip():
                messagebox.showerror("Validation Error", f"{field.replace('_', ' ').title()} is required!")
                return False
        
        # Validate date format
        try:
            datetime.strptime(self.form_vars["appointment_date"].get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date format! Use YYYY-MM-DD")
            return False
        
        return True
    
    def get_appointment_form_data(self):
        """Get data from appointment form"""
        data = {}
        
        for field_name, var in self.form_vars.items():
            if field_name in ["patient_id", "doctor_id"]:
                # Extract ID from combo selection
                value = var.get().strip()
                if value and " - " in value:
                    data[field_name] = value.split(" - ")[0]
                else:
                    data[field_name] = value
            else:
                data[field_name] = var.get().strip()
        
        # Get patient and doctor names
        patient_selection = self.form_vars["patient_id"].get()
        if " - " in patient_selection:
            data["patient_name"] = patient_selection.split(" - ")[1]
        
        doctor_selection = self.form_vars["doctor_id"].get()
        if " - " in doctor_selection:
            data["doctor_name"] = doctor_selection.split(" - ")[1]
        
        # Get notes
        data["notes"] = self.notes_text.get("1.0", tk.END).strip()
        
        return data
    
    def clear_appointment_form(self):
        """Clear appointment form"""
        for var in self.form_vars.values():
            var.set("")
        
        self.notes_text.delete("1.0", tk.END)
        self.current_appointment_id = None
    
    def book_appointment(self):
        """Book new appointment"""
        if not self.validate_appointment_form():
            return
        
        try:
            appointment_data = self.get_appointment_form_data()
            
            if self.appointment_manager.add_appointment(appointment_data):
                messagebox.showinfo("Success", "Appointment booked successfully!")
                self.clear_appointment_form()
                if not self.quick_mode:
                    self.load_appointments()
                    self.load_calendar()
                else:
                    self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to book appointment!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error booking appointment: {str(e)}")
    
    def update_appointment(self):
        """Update existing appointment"""
        if not self.current_appointment_id:
            messagebox.showwarning("Warning", "No appointment selected for update!")
            return
        
        if not self.validate_appointment_form():
            return
        
        try:
            appointment_data = self.get_appointment_form_data()
            
            if self.appointment_manager.update_appointment(self.current_appointment_id, appointment_data):
                messagebox.showinfo("Success", "Appointment updated successfully!")
                self.clear_appointment_form()
                self.load_appointments()
                self.load_calendar()
            else:
                messagebox.showerror("Error", "Failed to update appointment!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating appointment: {str(e)}")
    
    def load_appointments(self):
        """Load appointments into list"""
        if self.quick_mode:
            return
        
        try:
            # Clear existing items
            for item in self.appointment_tree.get_children():
                self.appointment_tree.delete(item)
            
            # Load appointments
            appointments = self.appointment_manager.get_all_appointments()
            
            for appointment in appointments:
                self.appointment_tree.insert("", tk.END, values=(
                    appointment.get("id", ""),
                    appointment.get("patient_name", appointment.get("patient_id", "")),
                    appointment.get("doctor_name", appointment.get("doctor_id", "")),
                    appointment.get("appointment_date", ""),
                    appointment.get("appointment_time", ""),
                    appointment.get("appointment_type", ""),
                    appointment.get("status", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading appointments: {str(e)}")
    
    def load_calendar(self):
        """Load calendar view"""
        if self.quick_mode:
            return
        
        try:
            # Update calendar label
            month_year = self.current_date.strftime("%B %Y")
            self.calendar_label.config(text=month_year)
            
            # Get calendar data
            cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
            
            # Clear all buttons
            for btn in self.calendar_buttons.values():
                btn.config(text="", bg="SystemButtonFace", state=tk.DISABLED)
            
            # Fill calendar
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        continue
                    
                    btn = self.calendar_buttons[(week_num, day_num)]
                    btn.config(text=str(day), state=tk.NORMAL)
                    
                    # Check if there are appointments on this day
                    date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"
                    appointments = self.appointment_manager.get_appointments_by_date(date_str)
                    
                    if appointments:
                        btn.config(bg="lightblue")
                    else:
                        btn.config(bg="SystemButtonFace")
                    
                    # Highlight today
                    today = datetime.now()
                    if (day == today.day and 
                        self.current_date.month == today.month and 
                        self.current_date.year == today.year):
                        btn.config(bg="lightgreen")
                        
        except Exception as e:
            messagebox.showerror("Error", f"Error loading calendar: {str(e)}")
    
    def previous_month(self):
        """Navigate to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.load_calendar()
    
    def next_month(self):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.load_calendar()
    
    def go_to_today(self):
        """Navigate to current month"""
        self.current_date = datetime.now()
        self.load_calendar()
    
    def on_calendar_day_click(self, week, day):
        """Handle calendar day click"""
        btn = self.calendar_buttons[(week, day)]
        day_num = btn.cget("text")
        
        if not day_num:
            return
        
        try:
            selected_date = f"{self.current_date.year}-{self.current_date.month:02d}-{int(day_num):02d}"
            appointments = self.appointment_manager.get_appointments_by_date(selected_date)
            
            # Clear selected date tree
            for item in self.selected_date_tree.get_children():
                self.selected_date_tree.delete(item)
            
            # Update selected date frame title
            self.selected_date_frame.config(text=f"Appointments for {selected_date}")
            
            # Load appointments for selected date
            for appointment in appointments:
                self.selected_date_tree.insert("", tk.END, values=(
                    appointment.get("appointment_time", ""),
                    appointment.get("patient_name", appointment.get("patient_id", "")),
                    appointment.get("doctor_name", appointment.get("doctor_id", "")),
                    appointment.get("appointment_type", ""),
                    appointment.get("status", "")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading day appointments: {str(e)}")
    
    def on_appointment_search(self, *args):
        """Handle appointment search"""
        if self.quick_mode:
            return
        
        search_query = self.search_var.get().strip().lower()
        
        try:
            # Clear existing items
            for item in self.appointment_tree.get_children():
                self.appointment_tree.delete(item)
            
            # Load and filter appointments
            appointments = self.appointment_manager.get_all_appointments()
            
            for appointment in appointments:
                # Search in patient name, doctor name, or appointment ID
                if (not search_query or 
                    search_query in appointment.get("patient_name", "").lower() or
                    search_query in appointment.get("doctor_name", "").lower() or
                    search_query in appointment.get("id", "").lower()):
                    
                    # Apply status filter
                    status_filter = self.status_filter_var.get()
                    if status_filter == "All" or appointment.get("status", "") == status_filter:
                        self.appointment_tree.insert("", tk.END, values=(
                            appointment.get("id", ""),
                            appointment.get("patient_name", appointment.get("patient_id", "")),
                            appointment.get("doctor_name", appointment.get("doctor_id", "")),
                            appointment.get("appointment_date", ""),
                            appointment.get("appointment_time", ""),
                            appointment.get("appointment_type", ""),
                            appointment.get("status", "")
                        ))
                        
        except Exception as e:
            messagebox.showerror("Error", f"Error searching appointments: {str(e)}")
    
    def on_status_filter(self, event=None):
        """Handle status filter change"""
        self.on_appointment_search()
    
    def on_appointment_select(self, event):
        """Handle appointment selection"""
        selection = self.appointment_tree.selection()
        if selection:
            item = self.appointment_tree.item(selection[0])
            appointment_id = item['values'][0]
            self.edit_appointment(appointment_id)
    
    def edit_appointment(self, appointment_id):
        """Load appointment data for editing"""
        try:
            appointments = self.appointment_manager.get_all_appointments()
            appointment = next((a for a in appointments if a.get('id') == appointment_id), None)
            
            if appointment:
                self.current_appointment_id = appointment_id
                
                # Fill form with appointment data
                self.form_vars["patient_id"].set(f"{appointment.get('patient_id', '')} - {appointment.get('patient_name', '')}")
                self.form_vars["doctor_id"].set(f"{appointment.get('doctor_id', '')} - {appointment.get('doctor_name', '')}")
                self.form_vars["appointment_date"].set(appointment.get('appointment_date', ''))
                self.form_vars["appointment_time"].set(appointment.get('appointment_time', ''))
                self.form_vars["appointment_type"].set(appointment.get('appointment_type', ''))
                self.form_vars["status"].set(appointment.get('status', ''))
                
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", appointment.get('notes', ''))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading appointment data: {str(e)}")
    
    def edit_selected_appointment(self):
        """Edit selected appointment from list"""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to edit!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        self.edit_appointment(appointment_id)
    
    def delete_selected_appointment(self):
        """Delete selected appointment"""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to delete!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        patient_name = item['values'][1]
        appointment_date = item['values'][3]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the appointment for '{patient_name}' on {appointment_date}?\n\nThis action cannot be undone!"):
            try:
                if self.appointment_manager.delete_appointment(appointment_id):
                    messagebox.showinfo("Success", "Appointment deleted successfully!")
                    self.clear_appointment_form()
                    self.load_appointments()
                    self.load_calendar()
                else:
                    messagebox.showerror("Error", "Failed to delete appointment!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting appointment: {str(e)}")
    
    def mark_appointment_complete(self):
        """Mark selected appointment as complete"""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to mark as complete!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        
        try:
            if self.appointment_manager.update_appointment(appointment_id, {"status": "Completed"}):
                messagebox.showinfo("Success", "Appointment marked as completed!")
                self.load_appointments()
                self.load_calendar()
            else:
                messagebox.showerror("Error", "Failed to update appointment status!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating appointment: {str(e)}")
    
    def cancel_appointment(self):
        """Cancel selected appointment"""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to cancel!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        patient_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Cancel", 
                              f"Are you sure you want to cancel the appointment for '{patient_name}'?"):
            try:
                if self.appointment_manager.update_appointment(appointment_id, {"status": "Cancelled"}):
                    messagebox.showinfo("Success", "Appointment cancelled successfully!")
                    self.load_appointments()
                    self.load_calendar()
                else:
                    messagebox.showerror("Error", "Failed to cancel appointment!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error cancelling appointment: {str(e)}")
