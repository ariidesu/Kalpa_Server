import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

from api.database import player_database, users
from api.misc import check_email

server = None

def init_email():
    print("[SMTP] Initializing email server...")
    global server
    if SMTP_PORT == 25 or SMTP_PORT == 80:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    else:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)

    server.ehlo()
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("[SMTP] Email server initialized successfully.")

async def send_verification_email_to_user(email, verify_code, lang = "en"):
    if not email or not check_email(email):
        return "Email is invalid."
    
    verify = await player_database.fetch_one(users.select().where(users.c.email == email))
    if not verify:
        return "Email is not registered."

    try:
        global server
        title = {"en": "Project Kepler - Email Verification", "zh": "项目 Kepler - 邮件验证", "tc": "專案 Kepler - 郵件驗證", "jp": "プロジェクト Kepler - メール認証"}
        with open(f"api/web/verification_email_{lang}.html", "r", encoding="utf-8") as file:
            body = file.read()

        body = body.format(code=verify_code)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg['Subject'] = title.get(lang, title['en'])

        msg.attach(MIMEText(body, 'html'))

        try:
            server.sendmail(SMTP_USER, email, msg.as_string())
            print("Email sent to ", email)
        except Exception as e:
            print(f"Email error: {e}")

        return "Verification code sent. Please check your email."

    except Exception as e:
        print(f"Email error: {e}")
        return "Email sending failed."
    
async def send_password_reset_email_to_user(email, temp_password, lang = "en"):
    if not email or not check_email(email):
        return "Email is invalid."
    
    verify = await player_database.fetch_one(users.select().where(users.c.email == email))
    if not verify:
        return "Email is not registered."

    try:
        global server
        title = {"en": "Project Kepler - Password Reset", "zh": "项目 Kepler - 重置密码", "tc": "專案 Kepler - 重置密碼", "jp": "プロジェクト Kepler - パスワードリセット"}
        with open(f"api/web/password_reset_{lang}.html", "r", encoding="utf-8") as file:
            body = file.read()

        body = body.format(temp_password=temp_password)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg['Subject'] = title.get(lang, title['en'])

        msg.attach(MIMEText(body, 'html'))

        server.sendmail(SMTP_USER, email, msg.as_string())
        print("Password reset email sent to ", email)
        return "Password reset email sent. Please check your email."

    except Exception as e:
        print(f"Email error: {e}")
        return "Email sending failed."
    
async def send_account_name_email_to_user(email, username, lang = "en"):
    if not email or not check_email(email):
        return "Email is invalid."
    
    verify = await player_database.fetch_one(users.select().where(users.c.email == email))
    if not verify:
        return "Email is not registered."

    try:
        global server
        title = {"en": "Project Kepler - Account Name Retrieval", "zh": "项目 Kepler - 帐号名称找回", "tc": "專案 Kepler - 帳號名稱找回", "jp": "プロジェクト Kepler - アカウント名の取得"}
        with open(f"api/web/account_name_{lang}.html", "r", encoding="utf-8") as file:
            body = file.read()

        body = body.format(username=username)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg['Subject'] = title.get(lang, title['en'])

        msg.attach(MIMEText(body, 'html'))

        server.sendmail(SMTP_USER, email, msg.as_string())
        print("Account name email sent to ", email)
        return "Account name email sent. Please check your email."

    except Exception as e:
        print(f"Email error: {e}")
        return "Email sending failed."