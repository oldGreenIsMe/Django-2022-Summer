import random
import smtplib
from authlib.jose import jwt
from email.header import Header
from django.conf import settings
from email.mime.text import MIMEText


def sendVerifyCodeMethod(toEmail, mode):
    verifyCode = '%06d' % random.randint(0, 999999)
    verifyCodeNum = list(str(verifyCode))
    with open("./utils/verifyCode/verifyCode1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/verifyCode/verifyCode2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/verifyCode/verifyCode3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    with open("./utils/verifyCode/verifyCode4.html", 'r', encoding='utf-8') as f:
        input4 = f.read()
    if mode == 1:
        data = input1 + verifyCodeNum[0] + input3 + verifyCodeNum[1] + input3 + verifyCodeNum[2] + input3 + \
               verifyCodeNum[3] + input3 + verifyCodeNum[4] + input3 + verifyCodeNum[5] + input2
        message = MIMEText(data, 'html', 'utf-8')
        message['Subject'] = Header('墨书-账号注册验证码')     # 邮件主题
    else:
        data = input4 + verifyCodeNum[0] + input3 + verifyCodeNum[1] + input3 + verifyCodeNum[2] + input3 + \
               verifyCodeNum[3] + input3 + verifyCodeNum[4] + input3 + verifyCodeNum[5] + input2
        message = MIMEText(data, 'html', 'utf-8')
        message['Subject'] = Header('墨书-账号修改密码验证码')
    message['From'] = Header('墨书团队')                    # 邮件发送者
    message['To'] = Header(toEmail)
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", settings.SECRETS['email_key'])
    try:
        mail.sendmail("805659773@qq.com", [toEmail], message.as_string())
    except smtplib.SMTPRecipientsRefused:
        return -1
    return verifyCode


def inviteMemberSendMethod(invitorName, userName, userId, teamName, teamId, toEmail):
    verifyUrl = "http://stcmp.shlprn.cn/api/team/acceptInvitation"
    data = {'teamid': teamId, 'userid': userId, 'judge': 1}
    header = {'alg': 'HS256'}
    key = settings.SECRETS['signing']['key']
    token = jwt.encode(header=header, payload=data, key=key)
    dstUrl = verifyUrl + '?token=' + token.decode()
    with open("./utils/teamInvite/teamInvite1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/teamInvite/teamInvite2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/teamInvite/teamInvite3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    with open("./utils/teamInvite/teamInvite4.html", 'r', encoding='utf-8') as f:
        input4 = f.read()
    with open("./utils/teamInvite/teamInvite5.html", 'r', encoding='utf-8') as f:
        input5 = f.read()
    msg = input1 + userName + input2 + invitorName + input3 + teamName + input4 + dstUrl + input5
    message = MIMEText(msg, 'html', 'utf-8')
    message['Subject'] = Header('墨书-团队邀请邮件')
    message['From'] = Header('墨书团队')
    message['To'] = Header(toEmail)
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", settings.SECRETS['email_key'])
    mail.sendmail("805659773@qq.com", [toEmail], message.as_string())


def inviteMemberCheck(token):
    key = settings.SECRETS['signing']['key']
    data = jwt.decode(token, key)
    return data


def applyJoinMethod(adminName, userName, userId, teamName, teamId, toEmail):
    verifyUrl = "http://stcmp.shlprn.cn/api/team/acceptInvitation"
    data = {'teamid': teamId, 'userid': userId, 'judge': 2}
    header = {'alg': 'HS256'}
    key = settings.SECRETS['signing']['key']
    token = jwt.encode(header=header, payload=data, key=key)
    dstUrl = verifyUrl + '?token=' + token.decode()
    with open("./utils/applyJoin/applyJoin1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/applyJoin/applyJoin2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/applyJoin/applyJoin3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    with open("./utils/applyJoin/applyJoin4.html", 'r', encoding='utf-8') as f:
        input4 = f.read()
    with open("./utils/applyJoin/applyJoin5.html", 'r', encoding='utf-8') as f:
        input5 = f.read()
    msg = input1 + adminName + input2 + userName + input3 + teamName + input4 + dstUrl + input5
    message = MIMEText(msg, 'html', 'utf-8')
    message['Subject'] = Header('墨书-申请加入团队邮件')
    message['From'] = Header('墨书团队')
    message['To'] = Header(toEmail)
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", settings.SECRETS['email_key'])
    mail.sendmail("805659773@qq.com", [toEmail], message.as_string())


def deleteNotice(adminName, userName, teamName, toEmail):
    with open("./utils/deleteUser/deleteUser1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/deleteUser/deleteUser2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/deleteUser/deleteUser3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    with open("./utils/deleteUser/deleteUser4.html", 'r', encoding='utf-8') as f:
        input4 = f.read()
    data = input1 + userName + input2 + adminName + input3 + teamName + input4
    message = MIMEText(data, 'html', 'utf-8')
    message['Subject'] = Header('墨书-移出团队通知邮件')
    message['From'] = Header('墨书团队')        # 邮件发送者
    message['To'] = Header(toEmail)
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", settings.SECRETS['email_key'])
    mail.sendmail("805659773@qq.com", [toEmail], message.as_string())


def deleteTeamNotice(adminName, userName, teamName, toEmail):
    with open("./utils/deleteTeam/deleteTeam1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/deleteTeam/deleteTeam2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/deleteTeam/deleteTeam3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    with open("./utils/deleteTeam/deleteTeam4.html", 'r', encoding='utf-8') as f:
        input4 = f.read()
    data = input1 + userName + input2 + adminName + input3 + teamName + input4
    message = MIMEText(data, 'html', 'utf-8')
    message['Subject'] = Header('墨书-团队解散通知邮件')
    message['From'] = Header('墨书团队')        # 邮件发送者
    message['To'] = Header(toEmail)
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", settings.SECRETS['email_key'])
    mail.sendmail("805659773@qq.com", [toEmail], message.as_string())


def authorizeAdminNotice(adminName, userName, teamName, toEmail):
    with open("./utils/authorizeAdmin/authorizeAdmin1.html", 'r', encoding='utf-8') as f:
        input1 = f.read()
    with open("./utils/authorizeAdmin/authorizeAdmin2.html", 'r', encoding='utf-8') as f:
        input2 = f.read()
    with open("./utils/authorizeAdmin/authorizeAdmin3.html", 'r', encoding='utf-8') as f:
        input3 = f.read()
    with open("./utils/authorizeAdmin/authorizeAdmin4.html", 'r', encoding='utf-8') as f:
        input4 = f.read()
    data = input1 + userName + input2 + adminName + input3 + teamName + input4
    message = MIMEText(data, 'html', 'utf-8')
    message['Subject'] = Header('墨书-授权成为管理员通知邮件')
    message['From'] = Header('墨书团队')        # 邮件发送者
    message['To'] = Header(toEmail)
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("805659773@qq.com", settings.SECRETS['email_key'])
    mail.sendmail("805659773@qq.com", [toEmail], message.as_string())
