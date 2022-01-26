import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


# This is an example email function. There are other email libraries
# available such as ExchangeLib that may be easier/better to use.
def send_email(email_address, password):
    msg = MIMEMultipart()
    msg['Subject'] = 'Password Reset'
    msg['From'] = "service.account@site.com"
    msg['To'] = email_address
    html = f'<html>Your password has been reset to {password}.' + '''
        <br>Please login with it at the <a href="http://localhost/update-pw">home page</a>.
        <br>Note: This email was sent automatically.</html>
    '''
    body = f'Your password has been reset to {password}.' + '''
        \n\nPlease login with it at the home page: http://localhost/update-pw.
        \n\nNote: This email was sent automatically.
    '''
    body_attmnt = MIMEText(body, 'plain')
    html_attmnt = MIMEText(html, 'html')
    msg.attach(body_attmnt)
    msg.attach(html_attmnt)
    s = smtplib.SMTP('localhost', 25)
    s.sendmail(msg['From'], email_address, msg.as_string())
    s.quit()
