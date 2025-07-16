"""
PDF Generator for Hospital Management System
Generates patient reports and medical summaries with QR codes
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from utils.qr_generator import QRGenerator
from utils.file_io import PatientManager, AppointmentManager, OPDManager

class PDFGenerator:
    def __init__(self):
        self.qr_generator = QRGenerator()
        self.patient_manager = PatientManager()
        self.appointment_manager = AppointmentManager()
        self.opd_manager = OPDManager()
        self.output_dir = "generated_pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_patient_summary(self, patient_id: str) -> str:
        """Generate comprehensive patient summary PDF with QR code"""
        try:
            # Get patient data
            patient = self.patient_manager.get_patient_by_id(patient_id)
            if not patient:
                raise ValueError(f"Patient with ID {patient_id} not found")
            
            # Get related data
            appointments = self.appointment_manager.get_appointments_by_patient(patient_id)
            opd_visits = self.opd_manager.get_visits_by_patient(patient_id)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"patient_summary_{patient_id}_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate QR code for the PDF
            qr_data = f"Patient ID: {patient_id}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nFile: {filepath}"
            qr_path = self.qr_generator.generate_qr_code(qr_data, f"patient_{patient_id}_qr.png")
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            # Title and Hospital Info
            story.append(Paragraph("HOSPITAL MANAGEMENT SYSTEM", title_style))
            story.append(Paragraph("Patient Summary Report", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            # Patient Information Section
            story.append(Paragraph("PATIENT INFORMATION", heading_style))
            patient_data = [
                ['Patient ID:', patient.get('id', 'N/A')],
                ['Name:', patient.get('name', 'N/A')],
                ['Age:', str(patient.get('age', 'N/A'))],
                ['Gender:', patient.get('gender', 'N/A')],
                ['Phone:', patient.get('phone', 'N/A')],
                ['Registration Date:', patient.get('registration_date', 'N/A')],
                ['Address:', patient.get('address', 'N/A')],
                ['Emergency Contact:', patient.get('emergency_contact', 'N/A')]
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 20))
            
            # Appointments Section
            story.append(Paragraph("APPOINTMENT HISTORY", heading_style))
            if appointments:
                apt_data = [['Date', 'Time', 'Doctor', 'Status', 'Notes']]
                for apt in appointments:
                    apt_data.append([
                        apt.get('appointment_date', 'N/A'),
                        apt.get('appointment_time', 'N/A'),
                        apt.get('doctor_name', 'N/A'),
                        apt.get('status', 'N/A'),
                        apt.get('notes', 'N/A')[:50] + '...' if len(apt.get('notes', '')) > 50 else apt.get('notes', 'N/A')
                    ])
                
                apt_table = Table(apt_data, colWidths=[1.2*inch, 0.8*inch, 1.5*inch, 1*inch, 2*inch])
                apt_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(apt_table)
            else:
                story.append(Paragraph("No appointment history found.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # OPD Visits Section
            story.append(Paragraph("OPD VISIT HISTORY", heading_style))
            if opd_visits:
                opd_data = [['Visit Date', 'Time', 'Chief Complaint', 'Diagnosis', 'Treatment']]
                for visit in opd_visits:
                    opd_data.append([
                        visit.get('visit_date', 'N/A'),
                        visit.get('visit_time', 'N/A'),
                        visit.get('chief_complaint', 'N/A')[:30] + '...' if len(visit.get('chief_complaint', '')) > 30 else visit.get('chief_complaint', 'N/A'),
                        visit.get('diagnosis', 'N/A')[:30] + '...' if len(visit.get('diagnosis', '')) > 30 else visit.get('diagnosis', 'N/A'),
                        visit.get('treatment', 'N/A')[:30] + '...' if len(visit.get('treatment', '')) > 30 else visit.get('treatment', 'N/A')
                    ])
                
                opd_table = Table(opd_data, colWidths=[1*inch, 0.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
                opd_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(opd_table)
            else:
                story.append(Paragraph("No OPD visit history found.", styles['Normal']))
            
            story.append(Spacer(1, 30))
            
            # QR Code Section
            story.append(Paragraph("DOCUMENT VERIFICATION", heading_style))
            if os.path.exists(qr_path):
                qr_image = Image(qr_path, width=2*inch, height=2*inch)
                story.append(qr_image)
                story.append(Paragraph("Scan QR code for document verification", styles['Normal']))
            
            # Footer
            story.append(Spacer(1, 20))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            story.append(Paragraph("This is a computer-generated document.", footer_style))
            
            # Build PDF
            doc.build(story)
            self.qr_generator.generate_pdf_drive_qr(
            pdf_path=filepath,
            person_name=patient.get("name", "Unknown"),
            patient_id=patient_id
)

            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error generating patient summary PDF: {str(e)}")
    
    def generate_appointment_list(self, date: str = None) -> str:
        """Generate appointment list PDF for specific date or all appointments"""
        try:
            # Get appointments
            if date:
                appointments = self.appointment_manager.get_appointments_by_date(date)
                title_suffix = f" for {date}"
            else:
                appointments = self.appointment_manager.get_all_appointments()
                title_suffix = " - All Appointments"
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"appointment_list_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph(f"APPOINTMENT LIST{title_suffix}", title_style))
            story.append(Spacer(1, 20))
            
            # Appointments table
            if appointments:
                apt_data = [['ID', 'Patient ID', 'Patient Name', 'Date', 'Time', 'Doctor', 'Status']]
                for apt in appointments:
                    patient = self.patient_manager.get_patient_by_id(apt.get('patient_id', ''))
                    patient_name = patient.get('name', 'Unknown') if patient else 'Unknown'
                    
                    apt_data.append([
                        apt.get('id', 'N/A'),
                        apt.get('patient_id', 'N/A'),
                        patient_name,
                        apt.get('appointment_date', 'N/A'),
                        apt.get('appointment_time', 'N/A'),
                        apt.get('doctor_name', 'N/A'),
                        apt.get('status', 'N/A')
                    ])
                
                apt_table = Table(apt_data, colWidths=[0.8*inch, 1*inch, 1.5*inch, 1*inch, 0.8*inch, 1.2*inch, 0.8*inch])
                apt_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(apt_table)
            else:
                story.append(Paragraph("No appointments found.", styles['Normal']))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error generating appointment list PDF: {str(e)}")
    
    def generate_opd_report(self, date: str = None) -> str:
        """Generate OPD report PDF for specific date or all visits"""
        try:
            # Get visits
            if date:
                visits = [v for v in self.opd_manager.get_all_visits() if v.get('visit_date') == date]
                title_suffix = f" for {date}"
            else:
                visits = self.opd_manager.get_all_visits()
                title_suffix = " - All Visits"
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"opd_report_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph(f"OPD REPORT{title_suffix}", title_style))
            story.append(Spacer(1, 20))
            
            # Visits table
            if visits:
                visit_data = [['ID', 'Patient ID', 'Patient Name', 'Date', 'Time', 'Chief Complaint', 'Status']]
                for visit in visits:
                    patient = self.patient_manager.get_patient_by_id(visit.get('patient_id', ''))
                    patient_name = patient.get('name', 'Unknown') if patient else 'Unknown'
                    
                    visit_data.append([
                        visit.get('id', 'N/A'),
                        visit.get('patient_id', 'N/A'),
                        patient_name,
                        visit.get('visit_date', 'N/A'),
                        visit.get('visit_time', 'N/A'),
                        visit.get('chief_complaint', 'N/A')[:30] + '...' if len(visit.get('chief_complaint', '')) > 30 else visit.get('chief_complaint', 'N/A'),
                        visit.get('status', 'N/A')
                    ])
                
                visit_table = Table(visit_data, colWidths=[0.8*inch, 1*inch, 1.3*inch, 0.9*inch, 0.7*inch, 1.8*inch, 0.8*inch])
                visit_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(visit_table)
            else:
                story.append(Paragraph("No OPD visits found.", styles['Normal']))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error generating OPD report PDF: {str(e)}")
