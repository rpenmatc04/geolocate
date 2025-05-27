import smtplib
import threading

from email.mime.text import MIMEText
class EmailSender: 
    """
    Class to set up a SMTP server to constantly send messages from a sender
    """
    def __init__(self, sender, password, multithreaded=False, recepient="", port=587):
        self.sender = sender 
        self.recepient = recepient
        self.port = port  
        self.password = password 
        self.multithreaded = multithreaded 
        if self.multithreaded: 
            self.lock = threading.Lock()

        self.mailserver = self.connect()

    def change_recepient(self, recepient):
        self.recepient = recepient 

    def quit(self): 
        self.mailserver.quit()

    def connect(self):
        server = smtplib.SMTP("smtp.gmail.com", self.port, timeout=10)
        server.starttls()
        server.login(self.sender, self.password)
        return server

    def send_synch_message(self, subject, body):
        message = MIMEText(body)
        message["From"] = self.sender
        message["To"] = self.recepient
        message["Subject"] = subject
        
        if self.multithreaded:
            # SMTP currently does not offer true multithreading without creating new connections (which take time)
            """
            with self.lock:
                self.mailserver.send_message(message)
            """ 
            with smtplib.SMTP("smtp.gmail.com", self.port) as temp_mailserver:
                temp_mailserver.starttls()
                temp_mailserver.login(self.sender, self.password)
                temp_mailserver.send_message(message)
        else: 
            try:
                self.mailserver.send_message(message)
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPException, OSError) as e:
                self.reconnect()
                self.mailserver.send_message(message)

    def reconnect(self):
        self.mailserver.quit()
        self.mailserver = self.connect()