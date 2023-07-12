import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx
from httpx import AsyncClient

from config import EMAIL_LOGIN, EMAIL_PASS, CLIENT_APP_URL, SECRET_KEY
from auth_exceptions import ConnectionToGmailException


CLIENT_SERVER = AsyncClient(base_url=CLIENT_APP_URL)

html = """"
<!DOCTYPE html>
<html lang="en">
<head>
<title> Verify you account!
</title>
</head>
<body>
<h1>%(code)s</h1>
</body>
</html>
"""


async def send_verify_email(email: str, reg_token: str):
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.starttls()
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your account!"
    message["From"] = EMAIL_LOGIN
    message["To"] = email
    message.attach(MIMEText(reg_token, 'plain'))
    message.attach(MIMEText(html % {'code': reg_token}, 'html'))
    for i in range(5):
        try:
            mail.login(EMAIL_LOGIN, EMAIL_PASS)
            mail.sendmail(EMAIL_LOGIN, email, message.as_string())
            break
        except Exception:
            if i == 4:
                raise ConnectionToGmailException
        finally:
            mail.quit()


async def send_verify_phone(phone: str, reg_token: str):
    pass


async def send_user(user, url):
    url = httpx.URL(path=url)
    print(user)
    rp_req = CLIENT_SERVER.build_request(
        'POST', url,
        content=user
    )
    rp_req.headers['secret-key'] = SECRET_KEY
    await CLIENT_SERVER.send(rp_req)


if __name__ == '__main__':
    pass
