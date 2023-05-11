'''
Author: AugustTheodor
Date: 2021-12-09 16:06:50
LastEditors: AugustTheodor
LastEditTime: 2022-01-28 17:16:08
Description: Aurora Models
'''
from ast import In
from enum import auto
import uuid
from django.db import models
from django.db.models.deletion import CASCADE, SET_DEFAULT, SET_NULL
from django.db.models.fields import IntegerField
from django.forms import DateTimeField
from pytz import timezone
from aurora_etc import comb, constants

# Create your models here.
class Aurora_User_Model(models.Model):
    #用户的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID) #主键 COMB
    user_name=models.CharField(max_length=20,blank=False) #昵称不超过10个汉字
    himg=models.CharField(max_length=100,default="") #头像
    bimg=models.CharField(max_length=100,default="") #个人主页背景图片
    ban=models.BooleanField(default=False) #封禁状态
    user_id=models.UUIDField(default=uuid.uuid4,unique=True) #展示用的id
    user_login_name=models.CharField(max_length=30,blank=False,default=None) #登陆名
    user_login_pwd=models.CharField(max_length=32,blank=False,default=None) #密码，MD5加密之后
    user_login_salt=models.CharField(max_length=10,default="sd4fds89f") #盐
    user_date_create=models.DateTimeField(auto_now_add=True) #创建时间
    user_signature=models.CharField(max_length=40,default="她什么都没说哦。")
    user_setting_allow_follow_explore=models.BooleanField(default=True) #是否允许查看关注和被关注列表
    digit_following=models.IntegerField(default=0) #关注
    digit_followed=models.IntegerField(default=0) #被关注
    digit_article=models.IntegerField(default=0) #发帖数量
    digit_group=models.IntegerField(default=0) #加入小组的数量
    digit_last_up=models.DateTimeField(null=True) #最后一次顶的时间
    m2m_user_group=models.ManyToManyField("Aurora_Group_Model",through="Aurora_M2M_User_Group_Model") #一些解释器语言总知道如何逼死强迫症^ ^
    m2m_follow=models.ManyToManyField("Aurora_User_Model",through="Aurora_M2M_User_User_Follow_Model") #关注的多对多关系
    class Meta():
        db_table="aurora_user"

class Aurora_Group_Model(models.Model):
    #话题小组的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    group_img=models.CharField(max_length=100,default="") #小组头像
    group_date_create=models.DateTimeField(auto_now_add=True)
    group_member=models.IntegerField(default=0) #人数统计
    group_id=models.UUIDField(default=uuid.uuid4,unique=True)
    group_member_name=models.CharField(max_length=10,default="个用户") #后缀
    group_title=models.CharField(max_length=40,unique=True) #组名，最多20汉字，且取名唯一
    group_report=models.CharField(max_length=200,default="") #举报自定义理由列表，空格分隔
    group_introduction=models.CharField(max_length=500,default="") #介绍
    group_color=models.CharField(max_length=10,default="#FFAB1A") #背景颜色
    group_join_type=models.IntegerField(default=constants.Group_Join_Type.Apply) #加入方式
    group_join_type_content=models.CharField(max_length=20,default="") #条件
    m2m_admin=models.ManyToManyField("Aurora_User_Model",through="Aurora_M2M_Group_Admin_User_Model")
    class Meta():
        db_table="aurora_group"

class Aurora_Article_Model(models.Model):
    #帖子的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    article_type=models.IntegerField(default=0) #文章类型 0公开 1版权 2私密
    article_sign=models.IntegerField(default=constants.Article_Sign.Normal) #文章标志 详情参见constants Article_Sign类
    article_id=models.UUIDField(default=uuid.uuid4,unique=True) #一个UUID，避免枚举，保证唯一
    article_create_time=models.DateTimeField(auto_now_add=True)
    article_img_list=models.CharField(max_length=1000,default=None,null=True) #图片列表
    article_title=models.CharField(max_length=100,null=True) #帖子名，最长不超过五十汉字
    article_author=models.ForeignKey(Aurora_User_Model,on_delete=SET_NULL,null=True,related_name="f_author") #作者，一个外键，这里使用SET_NULL记得取出数据时要做处理
    article_group=models.ForeignKey(Aurora_Group_Model,on_delete=SET_NULL,null=True) #炸组之后是需要一个废旧帖子收容装置滴^^
    article_content=models.CharField(max_length=10000) #帖子最长5000汉字
    article_origin=models.ForeignKey("Aurora_Article_Model",on_delete=CASCADE,null=True) #转发的源帖子
    m2m_prefer=models.ManyToManyField("Aurora_User_Model",through="Aurora_M2M_Prefer_Article_Model",related_name="f_prefer_author") #点赞的外键
    class Meta():
        db_table="aurora_article"
        ordering=['-article_create_time']

class Aurora_Article_Comment_Model(models.Model):
    #回帖的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    prefer=models.IntegerField(default=0) #点赞数量
    comment_id=models.UUIDField(default=uuid.uuid4,unique=True) #一个UUID，避免枚举，保证唯一
    comment_create_time=models.DateTimeField(auto_now_add=True)
    comment_author=models.ForeignKey(Aurora_User_Model,on_delete=SET_NULL,null=True) #作者
    comment_content=models.CharField(max_length=3000,null=True) #回复最长一千五百汉字
    comment_article=models.ForeignKey(Aurora_Article_Model,on_delete=CASCADE,default="") #帖子都删了留回复干毛线
    comment_report=models.IntegerField(default=0)
    comment_img=models.CharField(max_length=50,default=None,null=True) #回复携带的图片
    reply_comment=models.ForeignKey("Aurora_Article_Comment_Model",on_delete=CASCADE,null=True) #如果它回复的是另一条回复
    class Meta():
        db_table="aurora_article_comment"
        ordering=['comment_create_time']

class Aurora_Summary_Model(models.Model):
    #列表的信息类
    #列表相当于作者暴露的一个接口、以及第三方构成的接口。由于个人发布的帖子不能被查看，可以将愿意公开的帖子放在列表中供其他人查看
    #公开的列表，收藏帖子之前需要征得作者同意
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    summary_create_time=models.DateTimeField(auto_now_add=True)
    summary_id=models.UUIDField(default=uuid.uuid4,unique=True)
    summary_author=models.ForeignKey(Aurora_User_Model,on_delete=SET_NULL,null=True) #列表的创建者
    summary_title=models.CharField(max_length=100) #列表名，最长不超过五十汉字
    summary_pic=models.CharField(max_length=100,default="") 
    summary_keyword=models.CharField(max_length=50) #关键字，由英文逗号隔开的关键字组
    summary_describe=models.CharField(max_length=200) #描述
    summary_type=models.IntegerField(default=0) #0公开 1私密
    m2m_article_summary=models.ManyToManyField("Aurora_Article_Model",through="Aurora_M2M_Article_Summary_Model")
    m2m_follow=models.ManyToManyField("Aurora_User_Model",through="Aurora_M2M_User_Follow_Summary_Model",related_name="f_follow_user") #关注
    class Meta():
        db_table="aurora_summary"

class Aurora_Vote_Model(models.Model): 
    #投票的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    vote_article=models.ForeignKey(Aurora_Article_Model,on_delete=CASCADE) #投票所属的帖子
    vote_name=models.CharField(max_length=200,default="投票") #投票的名字

class Aurora_Vote_Item_Model(models.Model):
    #投票选项的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    item_vote=models.ForeignKey(Aurora_Vote_Model,on_delete=CASCADE) #所属投票
    item_name=models.CharField(max_length=40) #选项名
    item_sum=models.IntegerField(default=0) #投票数量

class Aurora_Vote_Sub_Model(models.Model):
    #每一条投票的信息类
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    sub_vote=models.ForeignKey(Aurora_Vote_Model,on_delete=CASCADE) #所属投票
    sub_item_name=models.ForeignKey(Aurora_Vote_Item_Model,on_delete=CASCADE) #选项的名字
    sub_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE) #投票人

#==============------------ 以下是数据统计表，这些表经常被编辑，所以被拆分开来
#==============------------ ^ ^
#==============------------ 

class Aurora_Summary_Info_Model(models.Model):
    #列表的数据类
    comb=models.OneToOneField(Aurora_Summary_Model,primary_key=True,on_delete=CASCADE) #主键为列表表的外键
    summary_follow=IntegerField(default=0) #关注
    summary_dict=IntegerField(default=0) #收藏夹中文章数量
    class Meta():
        db_table="aurora_summary_info"

class Aurora_Article_Info_Model(models.Model):
    #帖子的点赞等数据类
    comb=models.OneToOneField(Aurora_Article_Model,related_name="info",primary_key=True,on_delete=CASCADE) #主键为帖子表的外键
    article_prefer=IntegerField(default=0) #点赞
    article_up=IntegerField(default=0) #顶
    article_transmit=IntegerField(default=0,null=True) #转发（如果是转发的数据就没有这一项）
    article_star=IntegerField(default=0) #收藏
    article_comment=IntegerField(default=0) #回复（不算楼中楼）
    article_report=IntegerField(default=0) #举报次数
    article_last_update=models.DateTimeField(auto_now=True) #上次修改时间
    class Meta():
        db_table="aurora_article_info"

#==============------------ 以下是多对多关系的表
#==============------------ ^ ^
#==============------------

class Aurora_M2M_User_Group_Model(models.Model):
    #多对多 用户对小组
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    m2m_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,null=True) #用户被删除之后这个M2M关系也没有存在的必要了
    m2m_group=models.ForeignKey(Aurora_Group_Model,on_delete=CASCADE,null=True)
    class Meta():
        db_table="aurora_m2m_user_group"

class Aurora_M2M_Article_Summary_Model(models.Model):
    #多对多 帖子对列表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    desc=models.CharField(max_length=100,default="")
    m2m_article=models.ForeignKey(Aurora_Article_Model,on_delete=CASCADE,null=True)
    m2m_summary=models.ForeignKey(Aurora_Summary_Model,on_delete=CASCADE,null=True) #列表没了这条记录就没有什么存在的意义了
    time=models.DateTimeField(auto_now_add=True,null=True)
    class Meta():
        db_table="aurora_m2m_article_summary"

class Aurora_M2M_User_Follow_Summary_Model(models.Model):
    #多对多 用户对收藏的列表 #关注的列表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    m2m_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,null=True)
    m2m_summary=models.ForeignKey(Aurora_Summary_Model,on_delete=CASCADE,null=True)
    class Meta():
        db_table="aurora_m2m_user_follow_summary"

class Aurora_M2M_User_User_Follow_Model(models.Model):
    #多对多 关注列表，用户对用户
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    m2m_be_followed=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="f_followed_user") #被关注者，我想着我该改一下字段名字，不然有点分不清了
    m2m_following=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="f_following_user") #关注者
    class Meta():
        db_table="aurora_m2m_user_user_follow"

class Aurora_M2M_User_User_Block_Model(models.Model):
    #多对多 拉黑列表，用户对用户
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    m2m_be_blocked=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="r_blocked_user") #被拉黑者
    m2m_blocking=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="r_blocking_user")
    class Meta():
        db_table="aurora_m2m_user_user_block"

class Aurora_M2M_Prefer_Article_Model(models.Model):
    #真是无聊的点赞类，本来想用枚举合并，但是最后为了方便后续还是分开写吧
    #点赞->帖子
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    prefer_article=models.ForeignKey(Aurora_Article_Model,on_delete=CASCADE)
    prefer_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE)
    class Meta():
        db_table="aurora_m2m_prefer_article"

class Aurora_M2M_Prefer_Comment_Model(models.Model):
    #点赞->主楼评论
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    prefer_comment=models.ForeignKey(Aurora_Article_Comment_Model,on_delete=CASCADE)
    prefer_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE)
    class Meta():
        db_table="aurora_m2m_prefer_comment"

#==============------------ 以下是暂存表
#==============------------ ^ ^
#==============------------ 如果以后能做的很大，估计要用上Redis吧。但是现在不需要呢

class Aurora_Temp_M2M_Message_Model(models.Model):
    #服务器不长期存储消息，只在另一方用户下线的时候暂存消息。
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    from_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="f_message_from_user")
    content=models.CharField(max_length=2000) #最多五百字吧，因为这是加密的内容会扩充很多
    time=models.DateTimeField(auto_now_add=True)
    image=models.CharField(max_length=100,default="")
    to_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="f_message_to_user")
    is_encrypt=models.BooleanField(default=False) #是否是私密信息
    class Meta():
        db_table="aurora_temp_message"

class Aurora_Temp_M2M_Comment_Notice_Model(models.Model):
    #通知：评论的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    to_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE)
    from_comment=models.ForeignKey(Aurora_Article_Comment_Model,on_delete=CASCADE)
    type=models.CharField(max_length=5,default=constants.Type.Article)
    class Meta():
        db_table="aurora_temp_comment_notice"

class Aurora_Temp_M2M_Notice_Model(models.Model):
    #通知：杂项通知的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    to_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="notice_to_user")
    content=models.CharField(max_length=100,default="")
    type=models.CharField(max_length=10,null=True)
    type_id=models.CharField(max_length=60) #如果有跳转，这就是跳转的typeid
    time=models.DateTimeField(auto_now_add=True,null=True)
    class Meta():
        db_table="aurora_temp_notice"
    
class Aurora_M2M_Group_Admin_User_Model(models.Model):
    #管理员的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    with_group=models.ForeignKey(Aurora_Group_Model,on_delete=CASCADE,related_name="admin_user_with_group")
    admin_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="admin_user")
    admin_type=models.CharField(max_length=32,default="管理员")
    class Meta():
        db_table="aurora_group_admin_user"

class Aurora_Invitation(models.Model):
    #邀请码
    code=models.UUIDField(default=uuid.uuid4,primary_key=True)
    used_by=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,null=True) #一开始就是空的 
    remark=models.CharField(max_length=200,default="") #备注，必填项目
    mail=models.CharField(unique=True,max_length=50) #接受邀请码的邮箱，并且一定是唯一的
    class Meta():
        db_table="aurora_invitation"

class Aurora_M2M_Admin_Log_Model(models.Model):
    #管理记录的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    with_group=models.ForeignKey(Aurora_Group_Model,on_delete=CASCADE,related_name="admin_with_group")
    admin_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="admin_log_user")
    operation=models.CharField(max_length=10)
    content=models.CharField(max_length=500)
    time=models.DateTimeField(auto_now_add=True,null=True) #创建时间
    class Meta():
        db_table="aurora_admin_log"

class Aurora_M2M_Report_Log_Model(models.Model):
    #举报记录的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    with_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="report_with_user",null=True)
    with_group=models.ForeignKey(Aurora_Group_Model,on_delete=CASCADE,related_name="report_with_group")
    with_id=models.CharField(max_length=40)
    with_type=models.CharField(max_length=5)
    with_reason=models.IntegerField(default=0) #举报理由对应小组设置的类型
    time=models.DateTimeField(auto_now_add=True,null=True) #创建时间
    class Meta():
        db_table="aurora_report_log"

class Aurora_M2M_User_Group_Block_Model(models.Model):
    #小组黑名单的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    m2m_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="block_with_user")
    m2m_group=models.ForeignKey(Aurora_Group_Model,on_delete=CASCADE,related_name="block_with_group")
    class Meta():
        db_table="aurora_user_group_block"

class Aurora_M2M_Apply_Log_Model(models.Model):
    #申请加入的表
    comb=models.CharField(max_length=32,primary_key=True,default=comb.Aurora_Comb_UUID.CombID)
    m2m_user=models.ForeignKey(Aurora_User_Model,on_delete=CASCADE,related_name="apply_with_user")
    m2m_group=models.ForeignKey(Aurora_Group_Model,on_delete=CASCADE,related_name="apply_with_group")
    content=models.CharField(max_length=500) #申请理由，最多五百个字
    class Meta():
        db_table="aurora_user_group_apply"

class Aurora_Version_Model(models.Model):
    #版本表
    version=models.CharField(max_length=50,primary_key=True) #版本号
    force=models.BooleanField(default=False) #是否强制更新版本
    time=models.TimeField(auto_now_add=True) #创建时间
    class Meta():
        db_table="aurora_version"

class Aurora_Meta_Model(models.Model):
    #存储杂项
    key=models.CharField(max_length=20,primary_key=True) 
    value=models.CharField(max_length=200)
    class Meta():
        db_table="aurora_meta"
    
