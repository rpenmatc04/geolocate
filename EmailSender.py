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

        self.mailserver = smtplib.SMTP("smtp.gmail.com",self.port)
        self.mailserver.starttls()
        self.mailserver.login(self.sender, self.password)

    def change_recepient(self, recepient):
        self.recepient = recepient 

    def quit(self): 
        self.mailserver.quit()

    def send_synch_message(self, subject, body):
        message = MIMEText(body)
        message["From"] = self.sender
        message["To"] = self.recepient
        message["Subject"] = subject
        
        if self.multithreaded:
            """
            SMTP currently does not offer true multithreading without creating new connections (which take time)

            with smtplib.SMTP("smtp.gmail.com", self.port) as temp_mailserver:
                temp_mailserver.starttls()
                temp_mailserver.login(self.sender, self.password)
                temp_mailserver.send_message(message)

            """

            with self.lock:
                self.mailserver.send_message(message)

        else: 
            self.mailserver.send_message(message)