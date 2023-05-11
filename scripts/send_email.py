#发送邮件-邀请码

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from aurora_main.models import *
import base64

def run():
    send_email("2223216740@qq.com","XJM")

def send_email(user,remark): #remark 备注，user 邮箱
    #简单加密一下
    b64=base64.b64encode(user.encode('utf-8'))
    b64=b64[3:]+b64[0:3] #移位一下
    invitation=Aurora_Invitation.objects.create(remark=remark,mail=b64) #生成邀请码
    EmailMultiAlternatives("Aurora破晓邀请码发送通知",
    "亲爱的用户，您好：\n您的邀请码为 {0} ，绑定邮箱为此邮箱，并且不能解绑。\n请您在以下链接中下载破晓APP\n {1} \n破晓社区诚待您的加入！\n破晓的Augustine".format(invitation.code,settings.DOMAIN+settings.APP_LATEST_DOWNLOAD),
    settings.EMAIL_HOST_USER,[user]).send()
