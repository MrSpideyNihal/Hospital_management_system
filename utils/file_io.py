"""
File I/O Manager for Hospital Management System
Handles all data persistence operations using JSON files
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class FileIOManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data from {filename}: {e}")
            return []
    
    def save_data(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Save data to JSON file"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False, default=str)
            return True
        except IOError as e:
            print(f"Error saving data to {filename}: {e}")
            return False
    
    def generate_id(self, data: List[Dict[str, Any]], prefix: str = "") -> str:
        """Generate unique ID for new records"""
        if not data:
            return f"{prefix}001"
        
        # Extract numeric part from existing IDs
        max_id = 0
        for item in data:
            if 'id' in item:
                id_str = item['id']
                if prefix and id_str.startswith(prefix):
                    numeric_part = id_str[len(prefix):]
                else:
                    numeric_part = id_str
                
                try:
                    numeric_id = int(numeric_part)
                    max_id = max(max_id, numeric_id)
                except ValueError:
                    continue
        
        return f"{prefix}{max_id + 1:03d}"
    
    def backup_data(self, filename: str) -> bool:
        """Create backup of data file"""
        try:
            source_path = os.path.join(self.data_dir, filename)
            if os.path.exists(source_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{filename.split('.')[0]}_backup_{timestamp}.json"
                backup_path = os.path.join(self.data_dir, backup_filename)
                
                with open(source_path, 'r', encoding='utf-8') as source:
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(source.read())
                return True
        except IOError as e:
            print(f"Error creating backup for {filename}: {e}")
        return False

class PatientManager:
    def __init__(self):
        self.file_io = FileIOManager()
        self.filename = "patients.json"
    
    def get_all_patients(self) -> List[Dict[str, Any]]:
        """Get all patients"""
        return self.file_io.load_data(self.filename)
    
    def add_patient(self, patient_data: Dict[str, Any]) -> bool:
        """Add new patient"""
        patients = self.get_all_patients()
        patient_data['id'] = self.file_io.generate_id(patients, "PAT")
        patient_data['registration_date'] = datetime.now().strftime("%Y-%m-%d")
        patients.append(patient_data)
        return self.file_io.save_data(self.filename, patients)
    
    def update_patient(self, patient_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update existing patient"""
        patients = self.get_all_patients()
        for i, patient in enumerate(patients):
            if patient['id'] == patient_id:
                patients[i].update(updated_data)
                return self.file_io.save_data(self.filename, patients)
        return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """Delete patient"""
        patients = self.get_all_patients()
        patients = [p for p in patients if p['id'] != patient_id]
        return self.file_io.save_data(self.filename, patients)
    
    def search_patients(self, query: str) -> List[Dict[str, Any]]:
        """Search patients by name, ID, or phone"""
        patients = self.get_all_patients()
        query = query.lower()
        results = []
        
        for patient in patients:
            if (query in patient.get('name', '').lower() or
                query in patient.get('id', '').lower() or
                query in patient.get('phone', '').lower()):
                results.append(patient)
        
        return results
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID"""
        patients = self.get_all_patients()
        for patient in patients:
            if patient['id'] == patient_id:
                return patient
        return None

class AppointmentManager:
    def __init__(self):
        self.file_io = FileIOManager()
        self.filename = "appointments.json"
    
    def get_all_appointments(self) -> List[Dict[str, Any]]:
        """Get all appointments"""
        return self.file_io.load_data(self.filename)
    
    def add_appointment(self, appointment_data: Dict[str, Any]) -> bool:
        """Add new appointment"""
        appointments = self.get_all_appointments()
        appointment_data['id'] = self.file_io.generate_id(appointments, "APT")
        appointment_data['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        appointments.append(appointment_data)
        return self.file_io.save_data(self.filename, appointments)
    
    def update_appointment(self, appointment_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update existing appointment"""
        appointments = self.get_all_appointments()
        for i, appointment in enumerate(appointments):
            if appointment['id'] == appointment_id:
                appointments[i].update(updated_data)
                return self.file_io.save_data(self.filename, appointments)
        return False
    
    def delete_appointment(self, appointment_id: str) -> bool:
        """Delete appointment"""
        appointments = self.get_all_appointments()
        appointments = [a for a in appointments if a['id'] != appointment_id]
        return self.file_io.save_data(self.filename, appointments)
    
    def get_appointments_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get appointments for specific date"""
        appointments = self.get_all_appointments()
        return [a for a in appointments if a.get('appointment_date') == date]
    
    def get_appointments_by_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get appointments for specific patient"""
        appointments = self.get_all_appointments()
        return [a for a in appointments if a.get('patient_id') == patient_id]

class DoctorManager:
    def __init__(self):
        self.file_io = FileIOManager()
        self.filename = "doctors.json"
    
    def get_all_doctors(self) -> List[Dict[str, Any]]:
        """Get all doctors"""
        return self.file_io.load_data(self.filename)
    
    def add_doctor(self, doctor_data: Dict[str, Any]) -> bool:
        """Add new doctor"""
        doctors = self.get_all_doctors()
        doctor_data['id'] = self.file_io.generate_id(doctors, "DOC")
        doctors.append(doctor_data)
        return self.file_io.save_data(self.filename, doctors)
    
    def update_doctor(self, doctor_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update existing doctor"""
        doctors = self.get_all_doctors()
        for i, doctor in enumerate(doctors):
            if doctor['id'] == doctor_id:
                doctors[i].update(updated_data)
                return self.file_io.save_data(self.filename, doctors)
        return False
    
    def delete_doctor(self, doctor_id: str) -> bool:
        """Delete doctor"""
        doctors = self.get_all_doctors()
        doctors = [d for d in doctors if d['id'] != doctor_id]
        return self.file_io.save_data(self.filename, doctors)

class OPDManager:
    def __init__(self):
        self.file_io = FileIOManager()
        self.filename = "opd_visits.json"
    
    def get_all_visits(self) -> List[Dict[str, Any]]:
        """Get all OPD visits"""
        return self.file_io.load_data(self.filename)
    
    def add_visit(self, visit_data: Dict[str, Any]) -> bool:
        """Add new OPD visit"""
        visits = self.get_all_visits()
        visit_data['id'] = self.file_io.generate_id(visits, "OPD")
        visit_data['visit_date'] = datetime.now().strftime("%Y-%m-%d")
        visit_data['visit_time'] = datetime.now().strftime("%H:%M:%S")
        visits.append(visit_data)
        return self.file_io.save_data(self.filename, visits)
    
    def update_visit(self, visit_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update existing visit"""
        visits = self.get_all_visits()
        for i, visit in enumerate(visits):
            if visit['id'] == visit_id:
                visits[i].update(updated_data)
                return self.file_io.save_data(self.filename, visits)
        return False
    
    def get_visits_by_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get visits for specific patient"""
        visits = self.get_all_visits()
        return [v for v in visits if v.get('patient_id') == patient_id]
    
    def get_todays_visits(self) -> List[Dict[str, Any]]:
        """Get today's visits"""
        today = datetime.now().strftime("%Y-%m-%d")
        visits = self.get_all_visits()
        return [v for v in visits if v.get('visit_date') == today]
