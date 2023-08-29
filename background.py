from app.model import *
from sqlalchemy import or_
import imaplib
import email
import re
import io
from email.header import decode_header
import pdfplumber
from datetime import datetime
from dateutil import parser
from PyPDF2 import PdfReader

IMAP_SERVER = 'imap.ionos.com'
EMAIL_ADDRESS = 'jobs@y8hr.com'
PASSWORD = 'Infiniti123??'
# MySQL Database Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_DATABASE = 'emails'

server = imaplib.IMAP4_SSL(IMAP_SERVER, port=993)
server.login(EMAIL_ADDRESS, PASSWORD)
server.select('INBOX')

# Get the current date in the format 'dd-Jun-YYYY'
current_date = datetime.now().strftime('%d-%b-%Y')
year = '2023'

# Update the search criteria to fetch emails from June 1st to the current date
search_criteria = f'(SINCE 01-Jan-{year} BEFORE {current_date})'
_, msg_ids = server.search(None, search_criteria)
# Get the most recent 20 email IDs
recent_msg_ids = msg_ids[0].split()


def extract_phone_number(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            phone_pattern = r'(?:(?:\+?\d{1,3}\s?)?(?:\(\d{1,4}\)\s?)?|(?:\+?\d{1,3}\s)?\d{1,4}[\s./-]?)?\(?(?:\d{2,3})\)?[\s./-]?\d{1,5}[\s./-]?\d{1,5}(?:[\s./-]?\d{1,5})?(?:[\s./-]?\d{1,5})?'
            phone_matches = re.findall(phone_pattern, page_text)
            cleaned_numbers = [re.sub(r'\D', '', num) for num in phone_matches]
            cleaned_numbers = [num for num in cleaned_numbers if num]
            if cleaned_numbers:
                for num in cleaned_numbers:
                    if len(num) >= 10:
                        return num
    return None

def extract_emails(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.findall(email_pattern, page_text)
            if email_matches:
                return email_matches

    return None


def extract_subject_info(subject):
    # Find the first occurrence of "-" in the subject
    dash_index = subject.find('-')

    if dash_index != -1:
        first_part = subject[:dash_index].strip()
        second_part = subject[dash_index + 1:].strip()

        # Check if second_part contains "Indeed" or "ZipRecuriter" and extract that part
        indeed_zip_match = re.search(r'\b(Indeed|ZipRecuriter)\b', second_part, re.IGNORECASE)
        if indeed_zip_match:
            second_part = indeed_zip_match.group(0)

        return first_part, second_part
    else:
        # If "-" is not found in the subject, return the entire subject in the first part
        return subject.strip(), ""


for msg_id in recent_msg_ids:
    _, msg_data = server.fetch(msg_id, '(RFC822)')
    raw_message = msg_data[0][1]
    message = email.message_from_bytes(raw_message)
    if '=?' in message.get('Subject'):
        continue
    sender_name = email.utils.parseaddr(message.get('From'))[0]
    subject = message.get('Subject')
    date_raw = message.get('Date')
    date_obj = parser.parse(date_raw).date()
    formatted_date = date_obj.strftime('%a, %d %b %Y')
    subject_part1, subject_part2 = extract_subject_info(subject)

    pdf_attachments = []

    for part in message.walk():
        if part.get_content_type() == 'application/pdf':
            filename = part.get_filename()
            decoded_filename = decode_header(filename)[0][0]
            if isinstance(decoded_filename, bytes):
                decoded_filename = decoded_filename.decode()
            pdf_attachments.append((decoded_filename, part.get_payload(decode=True)))

    for filename, payload in pdf_attachments:
        payload_file = io.BytesIO(payload)
        pdf_reader = PdfReader(payload_file)
        has_images = any('/XObject' in page['/Resources'] and page['/Resources']['/XObject'].get_object() for page in
                         pdf_reader.pages)
        if has_images:
            print(f"Skipping {filename} as it contains images")
            continue

        phone_number = extract_phone_number(payload_file)
        emails = extract_emails(payload_file)
        email_str = ", ".join(emails) if emails else ""


        existing_entry = Emails_data.query.filter(
            or_(
                Emails_data.sender_name == sender_name,
                Emails_data.sender_name.is_(None)
            ),
            or_(
                Emails_data.email == email_str,
                Emails_data.email.is_(None)
            ),
            Emails_data.subject_part1 == subject_part1,
            Emails_data.subject_part2 == subject_part2,
            Emails_data.formatted_date == formatted_date,
            Emails_data.file_name == filename,
            Emails_data.phone_number == phone_number
        ).first()

        if existing_entry is None:

          if phone_number is not None and emails is not None:
             email_entry = Emails_data(
               sender_name=sender_name,
               email=emails[0] if emails else 'No Email!',
               subject_part1=subject_part1,
               subject_part2=subject_part2,
               formatted_date=formatted_date,
               file_name=filename,
               file_content=payload,
               phone_number=phone_number,
               action='',
               status=None
             )

          db.session.add(email_entry)

    db.session.commit()

server.logout()

