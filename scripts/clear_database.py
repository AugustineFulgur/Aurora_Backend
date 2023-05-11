#清理数据库
from aurora_main.models import *

def run():
    comment=Aurora_Article_Comment_Model.objects.all()
    for i in comment:
        i.delete()
    article=Aurora_Article_Model.objects.all()
    for i in article:
        i.delete()
    user=Aurora_User_Model.objects.all()
    for i in user:
        i.digit_article=0
        i.save()
    
    