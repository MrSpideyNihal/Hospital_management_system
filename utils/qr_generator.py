"""
QR Code Generator for Hospital Management System
Now includes Google Drive upload and dynamic QR code generation
"""

import os
import pickle
import qrcode
from PIL import Image
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

class QRGenerator:
    def __init__(self):
        self.qr_dir = os.path.join("generated_pdfs", "qr_codes")
        os.makedirs(self.qr_dir, exist_ok=True)
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.service = self.authenticate_drive()

    def authenticate_drive(self):
        """Authenticate with Google Drive and return service object"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.scopes)
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def upload_pdf_to_drive(self, filepath: str) -> Optional[str]:
        """Uploads PDF to Google Drive and returns a public download URL"""
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return None

        metadata = {
            'name': os.path.basename(filepath),
            'mimeType': 'application/pdf'
        }
        media = MediaFileUpload(filepath, mimetype='application/pdf', resumable=True)
        file = self.service.files().create(body=metadata, media_body=media, fields='id').execute()

        self.service.permissions().create(
            fileId=file['id'],
            body={'role': 'reader', 'type': 'anyone'},
        ).execute()

        file_id = file.get('id')
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    def generate_qr_code(self, data: str, filename: str, size: int = 10, border: int = 4) -> str:
        """Generates a QR code image with the given data and filename"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            filepath = os.path.join(self.qr_dir, filename)
            img.save(filepath)
            return filepath

        except Exception as e:
            print(f"❌ Failed to generate QR code: {e}")
            return ""

    def generate_patient_qr(self, patient_id: str, additional_info: str = "") -> str:
        """QR with raw patient info"""
        qr_data = f"PATIENT_ID:{patient_id}"
        if additional_info:
            qr_data += f"\n{additional_info}"

        filename = f"patient_{patient_id}_qr.png"
        return self.generate_qr_code(qr_data, filename)

    def generate_document_qr(self, document_path: str, document_type: str = "DOCUMENT") -> str:
        """QR code for referencing local document path"""
        qr_data = f"{document_type}:{document_path}"
        filename = f"doc_{os.path.basename(document_path)}_qr.png"
        return self.generate_qr_code(qr_data, filename)

    def generate_custom_qr(self, data: str, filename: str) -> str:
        """Generic custom QR code"""
        return self.generate_qr_code(data, filename)

    def generate_appointment_qr(self, appointment_id: str, patient_id: str, date: str, time: str) -> str:
        """QR with appointment details"""
        qr_data = f"APPOINTMENT_ID:{appointment_id}\nPATIENT_ID:{patient_id}\nDATE:{date}\nTIME:{time}"
        filename = f"appointment_{appointment_id}_qr.png"
        return self.generate_qr_code(qr_data, filename)

    def generate_visit_qr(self, visit_id: str, patient_id: str) -> str:
        """QR with visit reference"""
        qr_data = f"VISIT_ID:{visit_id}\nPATIENT_ID:{patient_id}"
        filename = f"visit_{visit_id}_qr.png"
        return self.generate_qr_code(qr_data, filename)

    def generate_pdf_drive_qr(self, pdf_path: str, person_name: str, patient_id: str) -> Optional[str]:
        """
        Uploads PDF to Drive, generates QR for public link, and saves QR as Person_Name_PATID.png

        Args:
            pdf_path: Full path to PDF
            person_name: Name of the patient
            patient_id: Patient ID

        Returns:
            QR code file path
        """
        link = self.upload_pdf_to_drive(pdf_path)
        if not link:
            return None

        safe_name = person_name.replace(" ", "_")
        qr_filename = f"{safe_name}_{patient_id}.png"
        return self.generate_qr_code(link, qr_filename)

    def cleanup_old_qr_codes(self, days_old: int = 30):
        """Deletes QR codes older than N days"""
        try:
            import time
            now = time.time()
            for filename in os.listdir(self.qr_dir):
                filepath = os.path.join(self.qr_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if (now - file_time) > (days_old * 86400):
                        os.remove(filepath)
                        print(f"🗑️ Deleted old QR code: {filename}")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
