import aiosmtplib
from email.mime.text import MIMEText

class AsyncEmailSender: 
    """
    Class to set up a Asynchronous server to constantly send messages from a sender to a recepient
    """
    def __init__(self, sender, password, recepient="", port=587):

        self.sender = sender
        self.recipient = recepient
        self.port = port
        self.password = password
        self.host = "smtp.gmail.com" 

        self.mailserver = aiosmtplib.SMTP(hostname=self.host, port=self.port, start_tls=True)
    
    async def start(self): 
        self.mailserver.connect() 
        self.mailserver.login(self.sender, self.password)

    async def send_async_message(self, subject, body):
        message = MIMEText(body)
        message["From"] = self.sender
        message["To"] = self.recepient
        message["Subject"] = subject

        await self.mailserver.send_message(message)