import smtplib

from email.mime.text import MIMEText
class EmailSender: 
    """
    Class to set up a SMTP server to constantly send messages from a sender
    """
    def __init__(self, sender, password, recepient="", port=587):
        self.sender = sender 
        self.recepient = recepient
        self.port = port  
        self.password = password 

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
        
        self.mailserver.send_message(message)
