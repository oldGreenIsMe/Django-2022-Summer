import random
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from django.core.mail import send_mail


def sendVerifyCodeMethod(toEmail):
    verifyCode = '%06d' % random.randint(0, 999999)
    verifyCodeNum = list(str(verifyCode))
    with open("./utils/verifyCode/verifyCode1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/verifyCode/verifyCode2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/verifyCode/verifyCode3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    data = input1 + verifyCodeNum[0] + input3 + verifyCodeNum[1] + input3 + verifyCodeNum[2] + input3 +\
           verifyCodeNum[3] + input3 + verifyCodeNum[4] + input3 + verifyCodeNum[5] + input2
    message = MIMEText(data, 'html', 'utf-8')
    message['From'] = Header('墨书团队')          # 邮件发送者名字
    # message['To'] = Header('小蓝枣')            邮件接收者名字
    message['Subject'] = Header('墨书账号验证码')  # 邮件主题
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", "etmhscregstlbdgg")
    mail.sendmail("805659773@qq.com", [toEmail], message.as_string())
    return verifyCode
