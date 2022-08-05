import yagmail,random,time #导入 yagmail , random 和 time 库
ss = input("您的昵称：")#询问用户昵称
yonghu = input("您的邮箱：")#询问用户邮箱
key = random.randint(0,999999)#设置验证码
yag = yagmail.SMTP( user="**邮箱账号**", password="**邮箱密码或授权码**", host='**邮箱SMTP服务器**')#链接邮箱服务器发信
subject = [" JunJun.Tec 验证码"]
contents = ['''
<table style="width: 99.8%; height: 95%;">
    <tbody>
        <tr>
            <td id="QQMAILSTATIONERY" style="background:url(https://rescdn.qqmail.com/bizmail/zh_CN/htmledition/images/xinzhi/bg/a_02.jpg) no-repeat #fffaf6; min-height:550px; padding:100px 55px 200px 100px; ">
            <div style="text-align: center;"><font>{},您好！&nbsp;</font></div>
            <div style="text-align: center;"><font><br>
                </font>
            </div>
            <div style="text-align: center;"><font>您的 JunJun.Tec 验证码/临时登录密码 为&nbsp;</font></div>
            <div style="text-align: center;"><font><br>
                </font>
            </div>
            <div style="text-align: center;"><font color="#ff0000"><b><u>{}</u></b></font></div>
            <div style="text-align: center;"><font><br>
                </font>
            </div>
            <div style="text-align: center;"><font>如非您本人操作无需理会。&nbsp;</font></div>
            <div style="text-align: center;"><font><br>
                </font>
            </div>
            <div style="text-align: center;"><font>感谢支持。</font></div>
            </td>
        </tr>
    </tbody>
</table>
<div><includetail><!--<![endif]--></includetail></div>
'''.format(ss,key)]#使用 ''' 嵌入HTML代码，使用 format 嵌入称呼(ss)与验证码(key)
yag.send(yonghu,subject, contents)#发送邮件
print("验证码邮件发送成功")
keypass2 = input("输入您的验证码：")#询问用户验证码
keypass = int(keypass2)#对 keypass2 进行 int 处理
if keypass == key:
    print('correct!')# 正确
else:
    print("Error!")# 错误
