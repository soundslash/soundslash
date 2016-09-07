
__version__ = "0.2"

import smtplib
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEBase import MIMEBase
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText
import tornado.template
import os

class EmailWrapper(object):
    def __init__(self):
        self.subject = "Not defined"
        self.sender = "noreply@soundslash.com"
        self.recipients = []
        self.body = ""

    def set_subject(self, subject):
        self.subject = subject

    def set_sender(self, sender):
        self.sender = sender

    def add_recipient(self, recipient):
        self.recipients.append(recipient)

    def set_body(self, template, args):
        loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__)+"/../", "templates"))
        self.body = loader.load(template).generate(**args)

    def send(self):

        try:
            session = smtplib.SMTP('radio-dychovka.sk', 25, timeout=5)
            session.login('bystricky', 'vajkovajkovite')
            # session.set_debuglevel(1)

            msg = MIMEText(self.body, 'html')
            msg['Subject'] = self.subject
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)
            result = session.sendmail(self.sender, self.recipients, msg.as_string())
            session.quit()
        except:
            result = False


        return result


