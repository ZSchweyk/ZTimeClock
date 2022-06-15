import mimetypes
import smtplib
from email.message import EmailMessage


def send_email(sender, password, recipient, body, subject, file_path):
    # Make file_path = "" if you don't want to send an attachment.
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(body)

    if file_path != "":
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type, mime_subtype = mime_type.split('/')
        with open(file_path, 'rb') as file:
            message.add_attachment(file.read(),
                                   maintype=mime_type,
                                   subtype=mime_subtype,
                                   filename=file_path.split("\\")[-1])

    mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
    mail_server.set_debuglevel(1)
    mail_server.login(sender, password)
    mail_server.send_message(message)
    mail_server.quit()




send_email("mrtaquito04@gmail.com", "Gmail1215!", "zschweyk@gmail.com", "This is a test email from Mr. Taguito", "TEST", "")

