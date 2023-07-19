import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json


def send_email(email,id):
    with open("key.json") as f:
        key = json.load(f)
    # smpt 서버와 연결
    gmail_smtp = "smtp.gmail.com"  # gmail smtp 주소
    gmail_port = 465  # gmail smtp 포트번호. 고정(변경 불가)
    smtp = smtplib.SMTP_SSL(gmail_smtp, gmail_port)

    # 로그인
    my_account = key["GOOGLE_ACCOUNT"]
    my_password = key["GOOGLE_PASSWORD"]
    smtp.login(my_account, my_password)

    # 메일을 받을 계정
    to_mail = email

    # 메일 기본 정보 설정
    msg = MIMEMultipart()
    msg["Subject"] = f"첨부 파일 확인 바랍니다"  # 메일 제목
    msg["From"] = my_account
    msg["To"] = to_mail

    # 메일 본문 내용
    content = "안녕하세요. \n\n\
    데이터를 전달드립니다.\n\n\
    감사합니다\n\n\
    "
    content_part = MIMEText(content, "plain")
    msg.attach(content_part)

    # 이미지 파일 추가
    image_name = f"{id}.jpg"
    with open(image_name, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-Disposition',
                       'attachment', filename=image_name)
        msg.attach(img)
    # img = bytearray(result)
    # img.add_header('Content-Disposition', 'attachment', filename= f"output_{id}.jpg")
    # msg.attach(img)
    # # 메일 전송
    smtp.sendmail(my_account, to_mail, msg.as_string())

    # smtp 서버 연결 해제
    smtp.quit()
