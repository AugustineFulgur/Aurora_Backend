'''
Author: AugustTheodor
Date: 2022-01-04 16:23:27
LastEditors: AugustTheodor
LastEditTime: 2022-01-06 16:29:13
Description: 运行在manage.py shell内部
'''


from django.db.models.expressions import Random
from aurora_main.models import *
from aurora_etc.comb import *

Aurora_Topic_Model.objects.create(comb=comb.Aurora_Comb_UUID.CombID(),comb=Aurora_Comb_UUID.CombID(),topic_title="回收站",topic_keyword="回收站,默认")
#默认小组
Aurora_User_Model.objects.create(comb=comb.Aurora_Comb_UUID.CombID(),comb=Aurora_Comb_UUID.CombID(),user_name="已注销")
#已注销
Aurora_Article_Model.objects.create(comb=comb.Aurora_Comb_UUID.CombID(),article_title="一个帖子",article_author=Aurora_User_Model.objects.all()[0],article_content="123456")
Aurora_Article_Info_Model.objects.create(comb=comb.Aurora_Comb_UUID.CombID(),comb=Aurora_Article_Model.objects.all()[0]) 
        