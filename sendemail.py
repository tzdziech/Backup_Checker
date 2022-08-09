""" Source FROM: https://python101.pythonlibrary.org/chapter17_smtplib.html
    Edited: Tomasz Zdziech
"""



import os
import smtplib
import sys

from configparser import ConfigParser
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

#----------------------------------------------------------------------
def send_email_with_attachment(subject, body_text, to_emails, cc_emails, bcc_emails, file_to_attach):
    """
    Send an email with an attachment
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "email.ini")
    header = 'Content-Disposition', 'attachment; filename="%s"' % file_to_attach
   
    # get the config
    if os.path.exists(config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
    else:
        print("Config not found! Exiting!")
        sys.exit(1)

    # extract server and from_addr from config
    host = cfg.get("smtp", "server")
    from_addr = cfg.get("smtp", "from_addr")
    username = cfg.get("smtp", "username")
    password = cfg.get("smtp", "password")

    # create the message
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    if body_text:
        msg.attach( MIMEText(body_text) )

    msg["To"] = ', '.join(to_emails)
    msg["cc"] = ', '.join(cc_emails)

    attachment = MIMEBase('application', "octet-stream")
    try:
        with open(file_to_attach, "rb") as fh:
            data = fh.read()
        attachment.set_payload( data )
        encoders.encode_base64(attachment)
        attachment.add_header(*header)
        msg.attach(attachment)
    except IOError:
        msg = f"Brak pliku zlacznika {file_to_attach}, zaznacz opcje zapisywania do pliku"
        print(msg)
        #sys.exit(1)

    emails = to_emails + cc_emails

    try:
        server = smtplib.SMTP(host, 587)
        server.starttls()
        server.login(username, password)
        server.sendmail(from_addr, emails, msg.as_string())
        server.quit()
        print("Email send")
    except Exception:
        print("Error sending:")

if __name__ == "__main__":
    emails = ["joachim.zdziech@gmail.com", ""]
    cc_emails = [""]
    bcc_emails = [""]

    subject = "IDZ SPAC JEST 1:27"
    body_text = "DO SPANIA PADALCU"
    path = "vpnlog\output.txt"
    send_email_with_attachment(subject, body_text, emails,
                               cc_emails, bcc_emails, path)

