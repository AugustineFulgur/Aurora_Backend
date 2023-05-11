'''
Author: AugustTheodor
Date: 2021-12-09 16:06:50
LastEditors: AugustTheodor
LastEditTime: 2022-01-25 17:37:01
Description: Modify it !!!!!!!!!!!!
'''
import ast
import base64
from datetime import datetime
from itertools import chain
from tkinter import E
from django.views import View
from Aurora_Backend.settings import IMAGE_DIR
from aurora_etc import constants
from aurora_etc import etcs
from aurora_etc.model_secondary_reference import Model_Secondary_Reference as Secondary, Safe_Words
from aurora_etc.model_secondary_reference import Safe_Words as Safe
from aurora_main.models import *
from aurora_etc.decorator import *
from aurora_etc.etcs import *
from django.db.models import Q
from django.utils import timezone
import hashlib
import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
# Create your views here.
# 操作的用户ID统一从后台session中取得^ ^

##心跳包
###参数 None
###方法 WEBsocket
###接收一个get参数，用于确认用户存活。当有消息在队列内时，发送响应更新私聊和消息提醒
@authorization_id
def heartbeat(request):
    while True:
        try:
            id=request.session['id'] #装饰器已经确保了有id
            user=Aurora_User_Model.objects.get(user_id=id)
        except:
            request.websocket.send("") #登陆失败，跳转到登录界面
        message=Aurora_Temp_M2M_Message_Model.objects.filter(to_user=user)
        comment=Aurora_Temp_M2M_Comment_Notice_Model.objects.filter(to_user=user)
        notice=Aurora_Temp_M2M_Notice_Model.objects.filter(to_user=user)
        if comment.count()+message.count()+notice.count()!=0: #有一条以上的新消息
            js={"message":Secondary.safe_notice_message(message),
                "comment":Secondary.safe_notice_comment(comment),
                "notice":Secondary.safe_notice_transmit(notice),
            }
            #message.delete()
            #notice.delete()
            #comment.delete()
            return js
        else:
            return None

##登陆
###参数 username 用户帐号 password 用户密码
###方法 POST/GET 
###会先确认sessionID是否过期，若不过期返回sessionID对应的id
###如果POST传入用户名和密码就是普通登陆流程，确认后返回id       
def login(request):
    if(not request.session.get('id')==None):
        return JsonResponse({'id':request.session.get('id')})
    try:
        user=Aurora_User_Model.objects.get(user_login_name=request.POST["loginname"]) #检验是否有用户
    except:
        return response404("用户名或密码错误")
    if user.ban==True:
        return response403("您已经被禁止登陆。")
    passwd=request.POST["password"]
    if user.user_login_pwd==hashlib.md5((passwd+user.user_login_salt).encode(encoding="utf-8")).hexdigest():
        #相等，鉴权成功
        request.session['id']=str(user.user_id) #存一个session
        return JsonResponse({'id':str(user.user_id)}) 
    else:
        return response403("用户名或密码错误")
        
##用户页信息，获取一个用户的信息
###参数 None
###方法 GET
@authorization_id
@parameter_verify("id",opt="GET") #确定指定的参数是否存在
def user_meta(request):
    try:
        id=request.session['id']
        user=Aurora_User_Model.objects.get(user_id=id)
    except:
        return response404("不存在的用户") #找不到用户
    return JsonResponse({"user_meta":Secondary.safe_user_model(user)})

##注册
###参数 code loginname username password #默认无绑定，绑邮箱让他们自己选好了
###方法 POST
###返回注册的id  
@parameter_verify("loginname","password","nickname","invitation",opt="POST")
def register(request):
    loginname=Safe.safe_number_letter(request.POST["loginname"])
    password=Safe.safe_number_letter_special(request.POST["password"])
    nickname=request.POST["nickname"]
    code=request.POST["invitation"]
    if(loginname!=None and password!=None and code!=None): #都通过了
        if len(loginname)>30:
            return response404("登陆用户名需小于30字符")
        if len(password)<8 or len(password)>20:
            return response404("密码长度需在8-20位之间")
        if len(nickname)>20:
            return response404("昵称长度需小于20字符")
        try:
            set=Aurora_Invitation.objects.get(code=code,used_by=None)
        except:
            return response404("邀请码无效")
        if Aurora_User_Model.objects.filter(user_login_name=loginname).count()!=0:
            #登陆名重复
            return response404("您的登陆名重复！")
        salt="" #盐，我还没想好选啥 这里可以随机处理
        md5=hashlib.md5()
        md5.update((password+salt).encode(encoding="utf8"))
        user=Aurora_User_Model.objects.create(ban=False,user_name=nickname,user_login_name=loginname,user_login_pwd=md5.hexdigest(),user_login_salt=salt)
        set.used_by=user
        set.save()
        return JsonResponse({"id":user.user_id})
    else:
        if loginname==None:
            return response403("登陆名由数字、字母组成")
        if password==None:
            return response403("密码由数字、字母、特殊字符组成")
        if code==None:
            return response403("您输入的邀请码格式有误")
        return response403("登陆名由数字、字母组成\n密码由数字、字母、特殊字符组成\n昵称由中英文、数字、特殊字符组成")

##获取一些广场的帖子
###参数 无
###方法 GET
###返回帖子列表
@authorization_id
@parameter_verify(opt="GET") #确定指定的参数是否存在
def stream_square(request):
    articles=Aurora_Article_Model.objects.all().order_by('?')[:10] #随机获取10个帖子
    li=[]
    for i in articles:
        stream=Secondary.safe_stream_article(i)
        li.append(stream)
    return JsonResponse(li,safe=False)

##获取帖子的详情（主楼）
###参数 id
###方法 GET
###返回帖子主楼的具体信息
@authorization_id
def article_detail(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        article=Aurora_Article_Model.objects.get(article_id=id)
        group=article.article_group
    except:
        return response404("找不到这个帖子哦~")
    info=Secondary.safe_article_detail(article)
    info['is_prefer']=Aurora_M2M_Prefer_Article_Model.objects.filter(prefer_user=user,prefer_article=article).count()!=0
    info['is_author']=article.article_author==user
    info['is_in_group']=Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user,m2m_group=group).count()!=0 or group==None
    if article.article_group==None:
        info['is_admin']=False
        info['is_top']=False
    else:
        info['is_admin']=Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()!=0
        info['is_top']=article.article_sign%constants.Article_Sign.APP_Top>=constants.Article_Sign.Group_Top
    return JsonResponse(info)

##删除帖子
###参数 无
###方法 GET
@authorization_id
def delete_article(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        article=Aurora_Article_Model.objects.get(article_id=id)
        group=article.article_group
        img=etcs.str2list(article.article_img_list)
    except:
        return response404("找不到这个帖子哦~")
    if article.article_author==user:
        for i in img:
            try:
                os.remove(IMAGE_DIR+i) #删除之前的文件
            except:
                pass
        article.delete() #作者删除，不会留记录
        return HttpResponse("操作成功")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()!=0:
        for i in img:
            try:
                os.remove(IMAGE_DIR+i) #删除之前的文件
            except:
                pass
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=article.article_author,content="您发布的帖子 "+article.article_title+" 已被管理员删除。")
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Delete,content=article.article_title)
        #存记录
        article.delete()
        return HttpResponse("操作成功，删帖记录已保存")
    return response403("您没有这个权限哦？")

##获取帖子的回复
###参数 p
###方法 GET
###根据页数返回对应的20条回复，不满则返回剩余回复
@authorization_id
def article_comment(request,id,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    try:
        article=Aurora_Article_Model.objects.get(article_id=id)
    except:
        return response404("帖子已经被删除啦~")
    p=int(p) #转一下类型
    if(Aurora_Article_Comment_Model.objects.filter(comment_article=article).count()<=20*p): #如果都获取完了，就返回空
        return JsonResponse([],safe=False)
    else:
        comments=Aurora_Article_Comment_Model.objects.filter(comment_article=article).order_by('comment_create_time')[20*p:20*(p+1)]
        li=[]
        for i in comments:
            item=Secondary.safe_comment(i)
            item['is_prefer']=Aurora_M2M_Prefer_Comment_Model.objects.filter(prefer_user=user,prefer_comment=i).count()==1
            li.append(item)
        return JsonResponse(li,safe=False)

##获取帖子的转发
###参数 p
###方法 GET
###根据页数返回对应的20条转发，不满则返回剩余转发
@authorization_id
def article_transmit(request,id,p):
    try:
        article=Aurora_Article_Model.objects.get(article_id=id)
    except:
        return response404("帖子已经被删除啦~")
    p=int(p) #转一下类型
    if(Aurora_Article_Model.objects.filter(article_origin=article).count()<=20*p): #如果都获取完了，就返回空
        return JsonResponse([],safe=False)
    transmits=Aurora_Article_Model.objects.filter(article_origin=article).order_by('article_create_time')[20*p:20*(p+1)]
    li=[] #这不来个调用块？这不来个调用块？pypy类rb^ ^!!!
    for i in transmits:
        item=Secondary.safe_transmit(i)
        li.append(item)
    return JsonResponse(li,safe=False)

##为帖子添加一个回复
###参数 comment （如果回复评论则有reply） type（评论回复文章的类型）
###方法 POST
@authorization_id
@parameter_verify("comment","type",opt="POST")
@char_verify("comment",opt="POST")
def article_set_comment(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        group=Aurora_Article_Model.objects.get(article_id=id).article_group
        article=Aurora_Article_Model.objects.get(article_id=id)
        article_info=Aurora_Article_Info_Model.objects.get(comb=article)
    except:
        return response404("这篇帖子好像已经被删除了？")
    if Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user,m2m_group=group).count()!=1 and group!=None: #在组内才能发言
        return response403("您没有权限发言哦？")
    if len(request.POST['comment'])>3000:
        return response404("您的发言太长了哦?需要3000字符以下，您超过了{0}字。".format(3000-len(request.POST['comment'])))
    article_info.article_comment+=1
    article_info.save() #摘要也要更新
    comment=Aurora_Article_Comment_Model.objects.create(comment_author=user,comment_article=article,comment_content=request.POST['comment'])
    if not user==article.article_author:
        Aurora_Temp_M2M_Comment_Notice_Model.objects.create(to_user=article.article_author,from_comment=comment,type=request.POST['type'])
    if("img" in request.POST): #图片的处理
        suffix=request.POST["img"].split(".") #后缀
        if not suffix[-1] in Safe_Words.SAFE_SUFFIX or len(suffix)>2:
            return response403("您选择的链接不合法！")
        if Safe_Words.safe_number_letter(suffix[0])!=None:
            comment.comment_content=comment.comment_content+"\n "
            comment.comment_img=request.POST['img']
            comment.save()
    if("reply" in request.POST):
        reply_comment=Aurora_Article_Comment_Model.objects.get(comment_id=request.POST['reply'])
        comment.reply_comment=reply_comment
        comment.save()
        if not reply_comment.comment_author==user and not reply_comment.comment_author==article.article_author: #回复的不是自己，且回复的不是楼主
            Aurora_Temp_M2M_Comment_Notice_Model.objects.create(to_user=reply_comment.comment_author,from_comment=comment,type=request.POST['type'])
    return JsonResponse(Secondary.safe_comment(comment)) #返回json然后被序列显示回去

##为帖子添加一个转发
###参数 transmit
###方法 POST
@authorization_id
@parameter_verify("transmit",opt="POST")
@char_verify("transmit",opt="POST")
def article_set_transmit(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        article_original=Aurora_Article_Model.objects.get(article_id=id)
        article_info=Aurora_Article_Info_Model.objects.get(comb=article_original)
        transmit=request.POST['transmit']
    except:
        return response404("找不到这个帖子哦？")
    if transmit=="" or transmit.isspace():
        return response404("您的内容不能为空哦？")
    if len(transmit)>10000:
        return response404("您为什么写了这么多字？转发的最高字符数为10000字。")
    article=Aurora_Article_Model.objects.create(article_title='',article_origin=article_original,article_content=transmit,article_author=user,article_group=None,article_img_list=None)
    article_info.article_transmit+=1
    article_info.save()
    user.digit_article+=1
    user.save()
    Aurora_Article_Info_Model.objects.create(comb=article,article_transmit=None) #创建shadow
    if article.article_author!=user: #不是同一人
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=article.article_author,content="您的帖子 "+article.article_title+" 被转发，转发内容为： "+transmit+" 。",type=constants.Type.Transmit,type_id=article.article_id)
    return HttpResponse("转发成功！")

##点赞，如果点了就取消
###参数 无
###方法 GET
@authorization_id
def article_set_like(request,id):
    try:
        article=Aurora_Article_Model.objects.get(article_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        info=Aurora_Article_Info_Model.objects.get(comb=article)
    except:
        return response404("帖子已经被删除啦~")
    li=Aurora_M2M_Prefer_Article_Model.objects.filter(prefer_article=article,prefer_user=user)
    if(li.count()==0): #无点赞
        Aurora_M2M_Prefer_Article_Model.objects.create(prefer_article=article,prefer_user=user)
        info.article_prefer=info.article_prefer+1
        info.save()
        return HttpResponse("True")
    else:
        li[0].delete()
        info.article_prefer=info.article_prefer-1
        info.save()
        return HttpResponse("False")

##评论点赞
### 参数 无
### 方法 GET
@authorization_id
def comment_set_like(request,id):
    try:
        comment=Aurora_Article_Comment_Model.objects.get(comment_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("回复已经被删除啦~")
    li=Aurora_M2M_Prefer_Comment_Model.objects.filter(prefer_comment=comment,prefer_user=user)
    if(li.count()==0):
        comment.prefer+=1
        comment.save()
        Aurora_M2M_Prefer_Comment_Model.objects.create(prefer_comment=comment,prefer_user=user)
        return HttpResponse("True")
    else:
        comment.prefer-=1
        comment.save()
        li[0].delete()
        return HttpResponse("False")

##评论删除
###参数 无
###方法 GET
@authorization_id
def comment_delete(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        comment=Aurora_Article_Comment_Model.objects.get(comment_id=id)
        group=comment.comment_article.article_group
    except:
        return response404("找不到这条回复哦？")
    if comment.comment_author==user:
        comment.delete() #作者删除，不会留记录
        return HttpResponse("操作成功")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()!=0:
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=comment.comment_author,content="您发布的回复 "+comment.comment_content+" 已被管理员删除。")
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Delete,content=comment.comment_content)
        #存记录
        comment.delete()
        return HttpResponse("操作成功，删帖记录已保存")
    return response403("您没有这个权限哦？")

##获取用户页面的信息（不是个人主页，是APP内“我的”页面的信息）
###参数 无
###方法 GET
@authorization_id
def user_detail(request,id):
    me=Aurora_User_Model.objects.get(user_id=request.session['id'])
    user=Aurora_User_Model.objects.get(user_id=id)
    s=Secondary.safe_user_meta(user)
    s['is_following']=Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_be_followed=user,m2m_following=me).count()==1
    s['is_blocking']=Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=user,m2m_blocking=me).count()==1
    return JsonResponse(s)

##获取用户关注的小组的信息
### 参数 无
### 方法 GET
@authorization_id
def user_follow_group(request):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    groups=Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user) #获取用户关注的所有小组
    li=[]
    for i in groups:
        print(i.m2m_group)
        li.append(Secondary.safe_group_item(i.m2m_group))
    return JsonResponse(li,safe=False)

##关注、取关用户
### 参数 无
### 方法 GET
@authorization_id
def user_follow_user(request,id):
    if id==request.session['id']:
        return response403("您不能关注自己哦？")
    try:
        me=Aurora_User_Model.objects.get(user_id=request.session['id'])
        user=Aurora_User_Model.objects.get(user_id=id)
    except:
        return response404("找不到这个用户哦？")
    follow_log=Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_be_followed=user,m2m_following=me)
    if follow_log.count()==1:
        #已经被关注了，取关
        follow_log.delete()
        me.digit_following-=1
        me.save()
        user.digit_followed-=1
        user.save()
    else:
        Aurora_M2M_User_User_Follow_Model.objects.create(m2m_be_followed=user,m2m_following=me)
        me.digit_following+=1
        me.save()
        user.digit_followed+=1
        user.save()
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=user,content="用户 "+me.user_name+" 关注了您。",type=constants.Type.User,type_id=me.user_id)
    return HttpResponse("操作成功！")

##拉黑、un拉黑（不知道怎么形容）用户
### 参数 无
### 方法 GET
@authorization_id
def user_block_user(request,id):
    if id==request.session['id']:
        return response403("您不能拉黑自己哦？")
    try:
        me=Aurora_User_Model.objects.get(user_id=request.session['id'])
        user=Aurora_User_Model.objects.get(user_id=id)
    except:
        return response404("找不到这个用户哦？")
    block_log=Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=user,m2m_blocking=me)
    if block_log.count()==1:
        #已经被拉黑了，放出
        block_log.delete()
        return HttpResponse("操作成功！")
    else:
        Aurora_M2M_User_User_Block_Model.objects.create(m2m_be_blocked=user,m2m_blocking=me)
        return HttpResponse("操作成功！若此用户存在违规行为，请发起投诉，我们将尽快处理")

##获取小组首页信息
### 参数 无
### 方法 GET
@authorization_id
def group_meta(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("找不到这个小组哦？")
    meta=Secondary.safe_group_meta(group)
    meta['is_follow']=Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user,m2m_group=group).count()!=0
    meta['is_admin']=Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()!=0
    return JsonResponse(meta)

##获取小组里最新的帖子
### 参数 无
### 方法 GET
@authorization_id
def group_fresh_article(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("找不到这个小组哦？")
    li=[]
    p=int(p)
    articles=Aurora_Article_Model.objects.filter(article_group=group).order_by("-info__article_last_update")[20*p:20*(p+1)]
    for i in articles:
        li.append(Secondary.safe_group_article(i))
    return JsonResponse(li,safe=False)

##获取小组里最热的帖子
###参数 无
###方法 GET
@authorization_id
def group_hot_article(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("找不到这个小组哦？")
    li=[]
    p=int(p)
    articles=Aurora_Article_Model.objects.filter(article_group=group).order_by("-info__article_comment")[20*p:20*(p+1)]
    for i in articles:
        li.append(Secondary.safe_group_article(i))
    return JsonResponse(li,safe=False)

##获取搜索最新的帖子
###参数 keyword
###方法 GET
@authorization_id
@parameter_verify("keyword",opt="GET")
def search_article(request,p):
    li=[]
    p=int(p)
    keyword=request.GET['keyword']
    if keyword=="":
        return response403("您输入了什么？")
    articles=Aurora_Article_Model.objects.filter(Q(article_title__contains=keyword)|Q(article_content__contains=keyword)).order_by("-article_create_time")[20*p:20*(p+1)]
    for i in articles:
        li.append(Secondary.safe_stream_article(i))
    return JsonResponse(li,safe=False)

##获取搜索小组
###参数 keyword
###方法 GET
@authorization_id
@parameter_verify("keyword",opt="GET")
def search_group(request,p):
    li=[]
    p=int(p)
    keyword=request.GET['keyword']
    if keyword=="":
        return response403("您输入了什么？")
    groups=Aurora_Group_Model.objects.filter(group_title__contains=keyword)
    for i in groups:
        li.append(Secondary.safe_group_list(i))
    return JsonResponse(li,safe=False)

##获取转发origin的rect
###参数 无
###方法 GET
@authorization_id
def article_rect(request,id):
    try:
        article=Aurora_Article_Model.objects.get(article_id=id)
        origin=article.article_origin
    except:
        return response404("找不到这个帖子哦？")
    s={}
    s['origin']=Secondary.safe_group_article(origin)
    s['article']=Secondary.safe_article_detail(article)
    return JsonResponse(s)

##获取收藏的rect
###参数 无
###方法 GET
@authorization_id
def user_summary_list(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    li=[]
    p=int(p)
    star_list=Aurora_Summary_Model.objects.filter(summary_author=user).order_by("summary_create_time")[20*p:20*(p+1)]
    for i in star_list:
        li.append(Secondary.safe_summary_meta(i))
    return JsonResponse(li,safe=False)

##创建一个收藏夹
###参数 name pic desc
###方法 POST
@authorization_id
@parameter_verify("name","desc","pic","type",opt="POST")
def create_summary(request):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    if(request.POST['name']=="" or request.POST['name'].isspace()):
        #内容为空或者pic为空
        return response404("标题不能为空或者空格哦？")
    if(request.POST['pic']==""):
        return response404("一定要选择一个封面哦？")
    Secondary.add_summary(user,request.POST["name"],request.POST["desc"],request.POST["pic"],request.POST["type"])
    return HttpResponse("创建成功！")

##获取关注的收藏夹的rect
###参数 无
###方法 GET
@authorization_id
def user_following_summary_list(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    li=[]
    p=int(p)
    star_list=Aurora_M2M_User_Follow_Summary_Model.objects.filter(follow_user=user)[20*p:20*(p+1)]
    for i in star_list:
        li.append(Secondary.safe_summary_meta(i.follow_summary))
    return JsonResponse(li,safe=False)

##小组关注与取关
### 参数 可能有content
### 方法 POST
@authorization_id
def group_follow(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("找不到这个小组哦？")
    is_follow=Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user,m2m_group=group)
    if Aurora_M2M_User_Group_Block_Model.objects.filter(m2m_user=user,m2m_group=group).count()==1:
        return HttpResponse("非常抱歉，您已经被此分组拉黑。") #拉黑的人直接返回
    if(is_follow.count()!=0): 
        group.group_member-=1
        group.save()
        user.digit_group-=1
        user.save()
        is_follow.delete()
        return HttpResponse("退出成功！")
    else: #加入小组的流程
        join_type=group.group_join_type
        join_content=group.group_join_type_content
        if join_type==constants.Group_Join_Type.No_Condition: #直接加入，可以直接加入
            group.group_member+=1
            group.save()
            user.digit_group+=1
            user.save()
            Aurora_M2M_User_Group_Model.objects.create(m2m_user=user,m2m_group=group)
            return HttpResponse("加入成功！")
        elif join_type==constants.Group_Join_Type.Followed:
            if user.digit_followed>=int(join_content):
                #满足被关注数量条件
                group.group_member+=1
                group.save()
                user.digit_group+=1
                user.save()
                Aurora_M2M_User_Group_Model.objects.create(m2m_user=user,m2m_group=group)
                return HttpResponse("加入成功！")
            else:
                return response403("很抱歉，您不满足该分组的加入条件：被关注数量超过"+join_content+"。")
        elif join_type==constants.Group_Join_Type.Answer:
            if "content" in request.POST:
                if request.POST["content"]==join_content:
                    #回答正确
                    group.group_member+=1
                    group.save()
                    user.digit_group+=1
                    user.save()
                    Aurora_M2M_User_Group_Model.objects.create(m2m_user=user,m2m_group=group)
                    return HttpResponse("加入成功！",)
                else:
                    return response403("您的参数有问题哦？")
        elif join_type==constants.Group_Join_Type.Apply:
            if "content" in request.POST:
                #存入申请列表内
                if Aurora_M2M_Apply_Log_Model.objects.filter(m2m_user=user,m2m_group=group).count()==0:
                    Aurora_M2M_Apply_Log_Model.objects.create(m2m_user=user,m2m_group=group,content=request.POST['content'])
                    return HttpResponse("您的申请已提交。",)
                else:
                    #已经申请过了
                    return response403("您已经申请过了哦？")
            else:
                return response403("您的参数有问题哦？")
    return HttpResponse(content="")
    
##上传图片
### 参数 无
### 方法 POST
@authorization_id
@parameter_verify(opt="POST")
def upload_image(request):
    '''
    if "img_count" in request.session:
        request.session["img_count"]+=1 #增加上传次数
        if request.session["img_count"]>100:
            return response403("您今天上传了太多图片！")
    else:
        request.session["img_count"]=1
    '''
    image=request.FILES.get("file")
    suffix=image.name.split(".")[-1] #后缀
    if not suffix in Safe_Words.SAFE_SUFFIX:
        return response403("上传的图片不符合格式！")
    else:
        file_name=comb.Aurora_Comb_UUID.CombID()+"."+suffix #文件名
        with open(IMAGE_DIR+file_name,"wb") as f:
            for chunk in image.chunks():
                f.write(chunk)
    return HttpResponse(file_name)

##发布帖子
### 参数 content title image type
### 方法 POST
@authorization_id
@parameter_verify("content","title","image","type",opt="POST")
@char_verify("content","title",opt="POST")
def create_article(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("找不到这个小组哦？")
    if Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user,m2m_group=group).count()==1: #用户已经进入小组
        if len(request.POST['content'])>10000:
            return response404("帖子主楼的最高字符数为10000字，您超过了{0}".format(len(request.POST['content'])-10000))
        if Secondary.add_article(request.POST['title'],request.POST['content'],request.POST['image'],user,group,int(request.POST['type']))!=False:
            return HttpResponse("发布成功！",)
        else:
            return response404("发送时发生错误，请联系管理员！")
    else:
        return response403("您没有权限发帖哦？")

##获取用户的头像和昵称
### 参数 无
### 方法 GET
@authorization_id
def short_user(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=id)
    except:
        return response404("这个用户不存在哦？")
    return JsonResponse({"author_nick":user.himg,"author_id":id,"author_name":user.user_name})

##获取小组的头像和名称
### 参数 无
### 方法 GET
@authorization_id
def short_group(request,id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("这个用户不存在哦？")
    return JsonResponse({"group_name":group.group_title,"group_pic":group.group_img,"group_id":group.group_id})

##发送聊天
### 参数 content,image,is_encrypt
### 方法 POST
@authorization_id
@parameter_verify("content","image","is_encrypt",opt="POST")
def set_message(request,id):
    try:
        to_user=Aurora_User_Model.objects.get(user_id=id)
        from_user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("这个用户不存在哦？")

    if(to_user.user_id==from_user.user_id):
        return response403("不能向自己发送消息")
    if(Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=from_user,m2m_blocking=to_user).count()!=0):
        #发送者被拉黑了
        return response403("您已经被对方拉黑")
    if(Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=to_user,m2m_blocking=from_user).count()!=0):
        #发送者拉黑了接收者
        return response403("您已经拉黑了对方")
    if len(request.POST['content'])>2000:
        return response404("您的私信字数过多哦？私信限制字数为2000字符，您超出了{0}".format(len(request.POST['content'])-2000))
    Aurora_Temp_M2M_Message_Model.objects.create(is_encrypt=request.POST['is_encrypt']=="true",from_user=from_user,to_user=to_user,content=request.POST['content'],image=request.POST['image'])
    return HttpResponse("发送成功！",)
    
##修改用户信息
### 参数 nick_name|signature|himg|bimg
### 方法 POST
@authorization_id
@parameter_verify(opt="POST")
def modify_user_data(request):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    if "nick_name" in request.POST:
        if len(request.POST['nick_name'])>20:
            return response404("昵称长度需小于20字符")
        user.user_name=request.POST['nick_name']
        user.save()
        return HttpResponse("修改成功！",)
    if "signature" in request.POST:
        if len(request.POST['signature'])>40:
            return response404("个人签名长度需小于40字符")
        user.user_signature=request.POST['signature']
        user.save()
        return HttpResponse("修改成功！",)
    if "himg" in request.POST:
        suffix=request.POST["himg"].split(".") #后缀
        if not suffix[-1] in Safe_Words.SAFE_SUFFIX or len(suffix)>2:
            return response403("您选择的链接不合法！")
        url=Safe_Words.safe_number_letter(suffix[0])
        if url!=False:
            try:
                os.remove(IMAGE_DIR+user.himg) #删除之前的文件
            except:
                pass #移除不了拉倒^ ^
            user.himg=request.POST['himg']
            user.save()
            return HttpResponse("修改成功！",)
        else:
            return response403("您选择的链接不合法！")
    if "bimg" in request.POST:
        suffix=request.POST["bimg"].split(".") #后缀
        if not suffix[-1] in Safe_Words.SAFE_SUFFIX or len(suffix)>2:
            return response403("您选择的链接不合法！")
        url=Safe_Words.safe_number_letter(suffix[0])
        if url!=False:
            try:
                os.remove(IMAGE_DIR+user.bimg) #删除之前的文件
            except:
                pass
            user.bimg=request.POST['bimg']
            user.save()
            return HttpResponse("修改成功！",)
        else:
            return response403("您选择的链接不合法！")
    if "password" in request.POST: #password 原密码 new 新密码
        salt="cats" #盐，我还没想好选啥
        md5=hashlib.md5()
        md5.update((request.POST['password']+salt).encode(encoding="utf8"))
        if user.user_login_pwd==md5.hexdigest(): #哈希对比下
            new_pass=hashlib.md5()
            new_pass.update((request.POST['new']+salt).encode(encoding="utf8"))
            user.user_login_pwd=new_pass.hexdigest()
            user.save()
            return HttpResponse("修改成功！")
        return response403("您输入的旧密码有误！")
    return response403("您的参数有误？")

##修改收藏夹信息
###方法 POST
###参数 desc|name|pic
@authorization_id
@parameter_verify(opt="POST")
def modify_summary_data(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=id)
    except:
        return response404("找不到这个收藏夹哦？")
    if not summary.summary_author==user:
        return response403("您没有权限提交此次修改哦？")
    if "desc" in request.POST:
        summary.summary_describe=request.POST["desc"]
        summary.save()
        return HttpResponse("操作成功！",)
    if "name" in request.POST:
        summary.summary_title=request.POST["name"]
        summary.save()
        return HttpResponse("操作成功！",)
    if "pic" in request.POST:
        link=Safe_Words.safe_link(request.POST["pic"])
        if link==False:
            return response403("您选择的链接不合法！")
        else:
            summary.summary_pic=request.POST["pic"]
            summary.save()
            return HttpResponse("操作成功！",)
    return response403("您的参数有误？")

##删除收藏夹
###方法 GET
###参数 无
@authorization_id
def delete_summary(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=id)
    except:
        return response404("找不到这个收藏夹哦？")
    if not summary.summary_author==user:
        return response403("您没有权限删除哦？")
    summary.delete()
    return HttpResponse("操作成功！",)

##关注/取关收藏夹
###方法 GET
###参数 无
@authorization_id
def summary_follow(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=id)
        info=Aurora_Summary_Info_Model.objects.get(comb=summary)
    except:
        return response404("找不到这个收藏夹哦？")
    summary_log=Aurora_M2M_User_Follow_Summary_Model.objects.filter(m2m_summary=summary,m2m_user=user)
    if summary_log.count()==0: #没关注
        Aurora_M2M_User_Follow_Summary_Model.objects.create(m2m_summary=summary,m2m_user=user)
        info.summary_follow+=1
        info.save()
    else:
        summary_log.delete()
        info.summary_follow-=1
        info.save()
    return HttpResponse("操作成功！",)
    
##修改收藏夹中帖子的收藏理由
###方法 POST
###参数 desc
@authorization_id
@parameter_verify("desc",opt="POST")
def summary_article_desc_modify(request,summary_id,article_id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=summary_id)
        article=Aurora_Article_Model.objects.get(article_id=article_id)
        m2m=Aurora_M2M_Article_Summary_Model.objects.get(m2m_article=article,m2m_summary=summary)
    except:
        return response404("收藏夹或文章不存在。")
    if not summary.summary_author==user:
        return response403("您没有权限操作哦？")
    if len(request.POST['desc'])>100:
        return response404("收藏理由最大字数为100，您的输入超长了。")
    m2m.desc=request.POST['desc']
    m2m.save()
    return HttpResponse("操作成功！",200)

##删除收藏夹中的帖子
###方法 GET
###参数 无
@authorization_id
def summary_article_delete(request,summary_id,article_id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=summary_id)
        article=Aurora_Article_Model.objects.get(article_id=article_id)
        m2m=Aurora_M2M_Article_Summary_Model.objects.get(m2m_article=article,m2m_summary=summary)
        info=Aurora_Summary_Info_Model.objects.get(comb=summary)
    except:
        return response404("收藏夹或文章不存在。")
    if not summary.summary_author==user:
        return response403("您没有权限操作哦？")    
    m2m.delete()
    info.summary_dict-=1
    info.save()
    return HttpResponse("操作成功！",200)

##给收藏夹增添帖子
###方法 POST
###参数 article_id desc
@authorization_id
@parameter_verify("desc",opt="POST")
def add_article_to_summary(request,summary_id,article_id):
    #查看归属权
    try:
        article=Aurora_Article_Model.objects.get(article_id=article_id)
        article_info=article.info
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=summary_id)
        info=Aurora_Summary_Info_Model.objects.get(comb=summary)
    except:
        return response404("收藏夹或文章不存在。")
    if not summary.summary_author==user:
        return response403("您无权编辑这个收藏夹！")
    if Aurora_M2M_Article_Summary_Model.objects.filter(m2m_article=article,m2m_summary=summary).count()!=0:
        return response403("这个帖子已经在收藏夹里了哦？")
    Aurora_M2M_Article_Summary_Model.objects.create(m2m_article=article,m2m_summary=summary,desc=request.POST["desc"])
    info.summary_dict+=1
    info.save()
    article_info.article_star+=1
    article_info.save()
    return HttpResponse("收藏成功！",)

##获取收藏夹的META信息（详情页信息）
###方法 GET
###参数 无
@authorization_id
def summary_meta(request,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        summary=Aurora_Summary_Model.objects.get(summary_id=id)
    except:
        return response404("找不到这个收藏夹哦？")
    m=Secondary.safe_summary_detail(summary)
    m['is_author']=summary.summary_author==user
    m['is_following']=Aurora_M2M_User_Follow_Summary_Model.objects.filter(m2m_user=user,m2m_summary=summary).count()==1
    return JsonResponse(m)

##获取收藏夹中文章的信息
###方法 GET
###参数 无
@authorization_id
def summary_detail(request,id,p):
    try:
        summary=Aurora_Summary_Model.objects.get(summary_id=id)
    except:
        return response404("找不到这个收藏夹哦？")
    p=int(p) #转一下类型
    if(Aurora_M2M_Article_Summary_Model.objects.filter(m2m_summary=summary).count()<=20*p): #如果都获取完了，就返回空
        return JsonResponse([],safe=False)
    else:
        articles=Aurora_M2M_Article_Summary_Model.objects.filter(m2m_summary=summary).order_by('-time')[20*p:20*(p+1)]
        li=[]
        for i in articles:
            item=Secondary.safe_summary_article(i)
            li.append(item)
        return JsonResponse(li,safe=False)

##顶文章
###方法 GET
###参数 无
@authorization_id
def up_article(request,id):
    try:
        article=Aurora_Article_Model.objects.get(article_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的文章不存在哦？")
    last_time=user.digit_last_up
    if last_time==None:
        user.digit_last_up=datetime.now() #更新时间
        user.save()
        article.info.save()
        return HttpResponse("顶帖成功~")
    else:
        time=datetime.now()
        if (time-last_time).seconds<180: #小于三分钟
            return response403("您的使用次数过于频繁哦？")
        else:
            user.digit_last_up=datetime.now() #更新时间
            user.save()
            article.info.save()
            article.save()
            return HttpResponse("顶帖成功~") 

##获取举报理由
###方法 GET
###参数 无
@authorization_id
def report_reasons(request,type,id):
    li=[]
    for i,j in constants.Report_Reason.reason.items():
        li.append({"reason":i,"id":j})
    if id=="" or type==constants.Type.User:
        return JsonResponse(li,safe=False)
    else:
        try:
            if type==constants.Type.Group:
                group=Aurora_Group_Model.objects.get(group_id=id)
            elif type==constants.Type.Article:
                group=Aurora_Article_Model.objects.get(article_id=id).article_group
            elif type==constants.Type.Comment:
                comment=Aurora_Article_Comment_Model.objects.get(comment_id=id)
                group=comment.comment_article.article_group
            else:
                group=None
        except:
            return response404("发生了一些错误哟？")
        if group==None:
            return JsonResponse(li,safe=False)
        if group.group_report=="":
            return JsonResponse(li,safe=False)
        else:
            group_li=etcs.str2list(group.group_report) #看见这些函数总会疑心一些安全性问题，hh
            for i,j in group_li.items():
                li.append({"reason":i,"id":j})
            return JsonResponse(li,safe=False)

##提交举报
###方法 POST
###参数 report_id
@authorization_id
@parameter_verify("reason_id",opt="POST")
def report_submit(request,type,id):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        if type==constants.Type.Group:
            group=Aurora_Group_Model.objects.get(group_id=id)
        elif type==constants.Type.Article:
            article=Aurora_Article_Model.objects.get(article_id=id)
            info=Aurora_Article_Info_Model.objects.get(comb=article)
            info.article_report+=1
            info.save()
            group=article.article_group
        elif type==constants.Type.Comment:
            comment=Aurora_Article_Comment_Model.objects.get(comment_id=id)
            comment.comment_report+=1
            comment.save()
            group=comment.comment_article.article_group
        else:
            return response403("未知类型？")
        reason_id=request.POST['reason_id']
    except:
        return response404("发生了一些错误哟？")
    #前面主要是保证id有效
    Aurora_M2M_Report_Log_Model.objects.create(with_group=group,with_id=id,with_user=user,with_type=type,with_reason=reason_id)
    return HttpResponse("您的举报已经被记录，感谢您对社区的支持。",)

##按热度获取被举报的帖子
###方法 GET
###参数 无
@authorization_id
def group_report_article(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    else:
        p=int(p)
        if Aurora_Article_Model.objects.filter(article_group=group).count()<20*p:
            return JsonResponse([],safe=False)
        articles=Aurora_Article_Model.objects.filter(article_group=group,info__article_report__gt=0).order_by('info__article_report')[20*p:20*(p+1)] #按照被举报数量排序
        li=[]
        for i in articles:
            li.append(Secondary.safe_report_article(i))
        return JsonResponse(li,safe=False)
    
##按时间获取举报
###方法 GET
###参数 无
@authorization_id
def group_report_log(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    else:
        p=int(p)
        if Aurora_M2M_Report_Log_Model.objects.filter(with_group=group).count()<20*p:
            return JsonResponse([],safe=False)
        li=[]
        logs=Aurora_M2M_Report_Log_Model.objects.filter(with_group=group).order_by('-time')[20*p:20*(p+1)]
        for i in logs:
            li.append(Secondary.safe_report_log(i))
        return JsonResponse(li,safe=False)

##处理举报的内容
###方法 GET
###参数 method
@authorization_id
@parameter_verify('method',opt="GET")
@char_verify('method',opt="GET")
def group_deal_report(request,report_id):
    try:
       user=Aurora_User_Model.objects.get(user_id=request.session['id'])
       report=Aurora_M2M_Report_Log_Model.objects.get(comb=report_id)
       group=report.with_group
    except:
        return response404("找不到该记录，可能已经被删除？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=Secondary.report_find_author_by_type_id(report)).count!=0:
        return response403("管理人员的帖子不可处理，请令其自行处理或组长另行处理")
    method=request.GET['method']
    if constants.Report_Deal_Type.Nothing in method:
        if not report.comb==None:
            report.delete()
    if constants.Report_Deal_Type.Delete in method:
        #删除
        try:
            Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Delete,content=Secondary.report_find_content_by_type_id(report))
            Secondary.report_find_thing_by_type_id(report).delete()
            if not report.comb==None:
                report.delete()
        except:
            return response404("该记录所属的对象已经被删除！")
    if constants.Report_Deal_Type.Ban in method:
        #拉黑，如果选了这个选项也就不会触发移出选项了
        if Aurora_M2M_User_Group_Block_Model.objects.filter(m2m_user=report.with_user,m2m_group=group).count()!=0:
            return response403("此人已经被移入黑名单。")
        else:
            Aurora_M2M_User_Group_Block_Model.objects.get(m2m_user=report.with_user,m2m_group=group)
            Aurora_M2M_User_Group_Model.objects.filter(m2m_user=report.with_user,m2m_group=group).delete() #这里删除原本的关注关系
            Aurora_Temp_M2M_Notice_Model.objects.create(to_user=report.with_user,content="很遗憾地通知您，您已被管理员加入分组 "+group.group_title+" 的黑名单中。")
            Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Block,content=report.with_user.user_id)
            if not report.comb==None:
                report.delete()
            return HttpResponse("操作成功。")
    if constants.Report_Deal_Type.Kick_Out in method:
        #移出
        if Aurora_M2M_User_Group_Model.objects.filter(m2m_user=report.with_user,m2m_group=group).count()==0:
            return response403("此人已经被移出分组了。")
        Aurora_M2M_User_Group_Model.objects.filter(m2m_user=report.with_user,m2m_group=group).delete() #这里删除原本的关注关系
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=report.with_user,content="很遗憾地通知您，您已被管理员移出分组 "+group.group_title+" 。")
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Remove,content=report.with_user.user_id)
        if not report.comb==None:
            report.delete()
    return HttpResponse("操作成功。")

##获取小组组长的meta
###方法 GET
###参数 无
@authorization_id
def group_admin_master(request,id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    else:
        master=Aurora_M2M_Group_Admin_User_Model.objects.get(admin_type=constants.Admin_Type.Master,with_group=group)
        return JsonResponse(Secondary.safe_member_meta(master.admin_user))

##获取小组管理员的meta
###方法 GET
###参数 无
@authorization_id
def group_admin_member(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    else:
        p=int(p)
        li=[]
        if Aurora_M2M_Group_Admin_User_Model.objects.filter(admin_type=constants.Admin_Type.Admin,with_group=group).count()<p*20:
            return JsonResponse(li,safe=False)
        admins=Aurora_M2M_Group_Admin_User_Model.objects.filter(admin_type=constants.Admin_Type.Admin,with_group=group)[p*20:(p+1)*20]
        for i in admins:
            li.append(Secondary.safe_member_meta(i.admin_user))
        return JsonResponse(li,safe=False)
        
##搜索小组成员
###方法 GET
###参数 search
@authorization_id
@parameter_verify("search",opt="GET")
def group_admin_search(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    else:
        p=int(p)
        li=[]
        if Aurora_M2M_User_Group_Model.objects.filter(m2m_group=group,m2m_user__user_name__contains=request.GET['search']).count()<p*20:
            return JsonResponse(li,safe=False)
        members=Aurora_M2M_User_Group_Model.objects.filter(m2m_group=group,m2m_user__user_name__contains=request.GET['search'])[p*20:(p+1)*20]
        for i in members:
            li.append(Secondary.safe_member_meta(i.m2m_user))
        return JsonResponse(li,safe=False)

##获取用户关注的人
###方法 GET
###参数 无
@authorization_id
def user_following_user(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    p=int(p)
    li=[]
    if Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_following=user).count()<p*20:
        return JsonResponse(li,safe=False)
    people=Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_following=user)[p*20:(p+1)*20]
    for i in people:
        li.append(Secondary.safe_member_meta(i.m2m_be_followed))
    return JsonResponse(li,safe=False)

##获取用户的粉丝
###方法 GET
###参数 无
@authorization_id
def user_followed_user(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    p=int(p)
    li=[]
    if Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_be_followed=user).count()<p*20:
        return JsonResponse(li,safe=False)
    people=Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_be_followed=user)[p*20:(p+1)*20]
    for i in people:
        li.append(Secondary.safe_member_meta(i.m2m_following))
    return JsonResponse(li,safe=False)

##小组黑名单查看
###方法 GET
###参数 无
@authorization_id
def group_admin_block_member(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    else:
        p=int(p)
        li=[]
        if Aurora_M2M_User_Group_Block_Model.objects.filter(m2m_group=group).count()<p*20:
            return JsonResponse(li,safe=False)
        block_users=Aurora_M2M_User_Group_Block_Model.objects.filter(m2m_group=group)[p*20:(p+1)*20]
        for i in block_users:
            li.append(Secondary.safe_member_meta(i.m2m_user))
        return JsonResponse(li,safe=False)

##小组人员处理（升职、踢出等）
###方法 POST
###参数 operation 
@authorization_id
@parameter_verify("operation",opt="POST")
def group_admin_manage_member(request,id,user_id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        member=Aurora_User_Model.objects.get(user_id=user_id)
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    if Aurora_M2M_User_Group_Model.objects.filter(m2m_user=member,m2m_group=group).count()!=1:
        #不在组里，不能操作
        return response403("被操作人不在组里哦？")
    user_rank=Aurora_M2M_Group_Admin_User_Model.objects.get(with_group=group,admin_user=user).admin_type
    operation=request.POST['operation']
    if operation=="UPGRADE":
        if user_rank==constants.Admin_Type.Master:
            if  Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=member).count()==0:
                Aurora_M2M_Group_Admin_User_Model.objects.create(with_group=group,admin_user=member,admin_type=constants.Admin_Type.Admin)
                return HttpResponse("操作成功",)
            else:
                return response404("她已经是管理员了哦？")
        else:
            Aurora_Temp_M2M_Notice_Model.objects.create(to_user=member,content="您已经成为分组 "+group.group_title+" 的管理员。")
            return response403("您不是组长哦？")
    if operation=="TRANSFER_MASTER": 
        if user_rank==constants.Admin_Type.Master:
            if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=member).count()==1:
                member_user=Aurora_M2M_Group_Admin_User_Model.objects.get(with_group=group,admin_user=member)
                member_user.admin_type=constants.Admin_Type.Master
                member_user.save()
                member_master=Aurora_M2M_Group_Admin_User_Model.objects.get(with_group=group,admin_user=user)
                member_master.admin_type=constants.Admin_Type.Admin
                member_master.save()
                Aurora_Temp_M2M_Notice_Model.objects.create(to_user=member,content="您已经成为分组 "+group.group_title+" 的组长。")
                return HttpResponse("分组转让成功！您已被降级至管理员。",)
            else:
                return response403("转移组长需要被转移人拥有管理员权限。")
        else:
            return response403("您不是组长哦？")
    if operation=="KICK_OUT":
        if Aurora_M2M_Group_Admin_User_Model.objects.filter(admin_user=user,admin_group=group).count()!=0:
            return response404("您没有这个权限哦！请先将管理员降职！")
        Aurora_M2M_User_Group_Model.objects.get(m2m_user=member,m2m_group=group).delete()
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=member,content="很遗憾地通知您，您已被管理员移出分组 "+group.group_title+" 。")
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Remove,content=member.user_id)
        return HttpResponse("操作成功")
    if operation=="BLOCK":
        if Aurora_M2M_User_Group_Block_Model.objects.filter(m2m_user=member,m2m_group=group).count()!=0:
            return response404("她已经在黑名单里了...")
        if Aurora_M2M_Group_Admin_User_Model.objects.filter(admin_user=user,admin_group=group).count()!=0:
            return response404("您没有这个权限哦！请先将管理员降职！")
        else:
            Aurora_M2M_User_Group_Block_Model.objects.get(m2m_user=member,m2m_group=group)
            Aurora_M2M_User_Group_Model.objects.filter(m2m_user=member,m2m_group=group).delete() #这里删除原本的关注关系
            Aurora_Temp_M2M_Notice_Model.objects.create(to_user=member,content="很遗憾地通知您，您已被管理员加入分组 "+group.group_title+" 的黑名单中。")
            Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Block,content=member.user_id)
            return HttpResponse("操作成功")
    if operation=="DISMISS":
        if user_rank==constants.Admin_Type.Master:
            if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=member).count()==1:
                Aurora_M2M_Group_Admin_User_Model.objects.get(with_group=group,admin_user=member).delete()
                return HttpResponse("操作成功")
            else:
                return response404("她本来就不是管理员哦？")
        else:
            return response403("您不是组长哦？")
    return response404("您的操作出了一点问题哦？")

##小组入组方式修改与浏览
###方法 POST 、GET
###参数 type content
@authorization_id
def admin_join_type(request,id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if request.method=="GET":
        return JsonResponse({"type":group.group_join_type,"content":group.group_join_type_content})
    try:
        type=request.POST['type']
    except:
        return response404("您的操作有问题哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    elif request.method=="POST" and "type" in request.POST and "content" in request.POST:
        group.group_join_type=type
        group.group_join_type_content=request.POST['content']
        group.save()
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Modify,content="修改了入组方式。")
        return HttpResponse("您的修改已生效。")
    else:
        return response404("您的操作有问题哦？")

##修改小组信息
###方法 POST
###参数 theme_color|member_name|introduction|group_pic
@authorization_id
def modify_group_data(request,id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    if "theme_color" in request.POST:
        group.group_color=request.POST['theme_color']
        group.save()
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Modify,content="修改了分组主题颜色")
        return HttpResponse("修改成功！",)
    if "member_name" in request.POST:
        group.group_member_name=request.POST['member_name']
        group.save()
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Modify,content="修改了分组组员名称")
        return HttpResponse("修改成功！",)
    if "introduction" in request.POST:
        group.group_introduction=request.POST['introduction']
        group.save()
        Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Modify,content="修改了分组简介")
        return HttpResponse("修改成功！",)
    if "group_pic" in request.POST:
        link=Safe_Words.safe_link(request.POST["group_pic"])
        if link==False:
            return response403("您选择的链接不合法！")
        else:
            group.group_img=request.POST["group_pic"]
            group.save()
            Aurora_M2M_Admin_Log_Model.objects.create(with_group=group,admin_user=user,operation=constants.Admin_Log_Operator.Modify,content="修改了分组头像")
            return HttpResponse("操作成功！",)
    return response404("您的输入有误哦？")

##查看小组管理日志
###方法 GET
###参数 无
def admin_group_log(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    p=int(p)
    li=[]
    if Aurora_M2M_Admin_Log_Model.objects.filter(with_group=group).count()<p*20:
        return JsonResponse(li,safe=False)
    log=Aurora_M2M_Admin_Log_Model.objects.filter(with_group=group)[p*20:(p+1)*20]
    for i in log:
        li.append(Secondary.safe_admin_log(i))
    return JsonResponse(li,safe=False)

##查看小组申请
###方法 GET
###参数 无
def admin_group_apply(request,id,p):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    p=int(p)
    li=[]
    if Aurora_M2M_Apply_Log_Model.objects.filter(m2m_group=group).count()<p*20:
        return JsonResponse(li,safe=False)
    log=Aurora_M2M_Apply_Log_Model.objects.filter(m2m_group=group)[p*20:(p+1)*20]
    for i in log:
        li.append(Secondary.safe_admin_apply(i))
    return JsonResponse(li,safe=False)

##管理员辞职
###方法 GET
###参数 无
@authorization_id
def admin_dismiss(request,id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    log=Aurora_M2M_Group_Admin_User_Model.objects.get(with_group=group,admin_user=user)
    if log.admin_type==constants.Admin_Type.Master:
        return response403("您需要先转让组长之后再辞职")
    else:
        log.delete()
        return HttpResponse("操作成功，感谢您为社区做出的贡献",)

##获取角色的动态（转发+广场帖子）
###方法 GET
###参数 无
@authorization_id
def user_trend(request,id,p):
    try:
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
        member=user=Aurora_User_Model.objects.get(id)
    except:
        return response404("您要找的用户不存在哦？")
    if Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=user,m2m_blocking=member).count()!=0:
        return response403("她已经拉黑您了...")
    else:
        p=int(p)
        li=[]
        if Aurora_Article_Model.objects.filter(article_author=member).count()<p*20:
            return JsonResponse(li,safe=False)
        articles=Aurora_Article_Model.objects.filter(article_author=member)[p*20:(p+1)*20]
        for i in articles:
            li.append(Secondary.safe_member_meta(i.m2m_user))
        return JsonResponse(li,safe=False)
        
##用户写动态
###方法 POST
###参数 content image type 
@authorization_id
@parameter_verify("content","image","type",opt="POST")
def create_trend(request):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    if len(request.POST['content'])>10000:
            return response404("动态的最高字符数为10000字，您超过了{0}".format(len(request.POST['content'])-10000))
    user.digit_article+=1
    user.save()
    article=Aurora_Article_Model.objects.create(article_type=int(request.POST['type']),article_title='',article_content=request.POST['content'],article_author=user,article_group=None,article_img_list=request.POST['image'])
    Aurora_Article_Info_Model.objects.create(comb=article)
    return HttpResponse("发布成功！",)

##获取APP置顶的帖子
###方法 GET
###参数 无
@authorization_id
def app_top_articles(request):
    top=Aurora_Article_Model.objects.filter(article_sign__gte=constants.Article_Sign.APP_Top)
    li=[]
    for i in top:
        s={}
        s['title']=i.article_title
        s['id']=i.article_id
        li.append(s)
    return JsonResponse(li,safe=False)

##获取分组置顶的帖子
###方法 GET
###参数 无
@authorization_id
def group_top_articles(request,id):
    try:
        group=Aurora_Group_Model.objects.get(group_id=id)
    except:
        return response404("找不到这个帖子哦？")
    top=Aurora_Article_Model.objects.filter(article_group=group,article_sign__range=(constants.Article_Sign.Group_Top,constants.Article_Sign.APP_Top))
    li=[]
    for i in top:
        s={}
        s['title']=i.article_title
        s['id']=i.article_id
        li.append(s)
    return JsonResponse(li,safe=False)

##获取小组排行榜（前三）
###方法 GET
###参数 无
@authorization_id
def app_group_rank(request):
    groups=Aurora_Group_Model.objects.all().order_by("-group_member")[:3]
    li=[]
    for i in groups:
        li.append(Secondary.safe_group_list(i))
    return JsonResponse(li,safe=False)

##获取用户关注的小组（列表版）
###方法 GET
###参数 无
@authorization_id
def user_detail_follow_group(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    p=int(p)
    li=[]
    if Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user).count()<p*20:
        return JsonResponse(li,safe=False)
    groups=Aurora_M2M_User_Group_Model.objects.filter(m2m_user=user)[p*20:(p+1)*20]
    for i in groups:
        li.append(Secondary.safe_group_list(i.m2m_group))
    return JsonResponse(li,safe=False)

##处理小组加入申请
###方法 POST
###参数 无 （method为AGREE REFUSE两种）
@authorization_id
def admin_deal_apply(request,group_id,apply_id,method):
    try:
        group=Aurora_Group_Model.objects.get(group_id=group_id)
        user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    except:
        return response404("您要找的分组不存在哦？")
    try:
        apply=Aurora_M2M_Apply_Log_Model.objects.get(comb=apply_id)
        apply_user=apply.m2m_user
    except:
        return response404("这条申请已经不存在了哟？是否有其他人已经处理过了？")
    if Aurora_M2M_Group_Admin_User_Model.objects.filter(with_group=group,admin_user=user).count()==0:
        return response403("您没有这个权限哦？")
    if method=="AGREE":
        if Aurora_M2M_User_Group_Model.objects.filter(m2m_user=apply_user,m2m_group=group).count()==0:
            #没有记录，这是个保险，以防修改入组方式之后重新处理
            group.group_member+=1
            group.save()
            apply_user.digit_group+=1
            apply_user.save()
            Aurora_M2M_User_Group_Model.objects.create(m2m_user=apply_user,m2m_group=group)
            apply.delete()
            Aurora_Temp_M2M_Notice_Model.objects.create(to_user=apply_user,content="恭喜，您对分组 {0} 的加入申请已经被通过。".format(group.group_title),type_id=group.group_id,type=constants.Type.Group)
            return HttpResponse("操作成功。")
        else:
            return response404("她已经加入了这个小组。")
    if method=="REFUSE":
        apply.delete()
        Aurora_Temp_M2M_Notice_Model.objects.create(to_user=apply_user,content="非常遗憾地通知您，您对分组 {0} 的加入申请被拒绝。".format(group.group_title),type_id=group.group_id,type=constants.Type.Group)
        return HttpResponse("操作成功。")
    return response404("您的操作有点问题哦？")

##历史帖子
###方法 GET
###参数 无
@authorization_id
def user_history_article(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    li=[]
    p=int(p)
    if Aurora_Article_Model.objects.filter(article_author=user).count()<p*20:
        return JsonResponse(li,safe=False)
    articles=Aurora_Article_Model.objects.filter(article_author=user)[p*20:(p+1)*20]
    for i in articles:
        li.append(Secondary.safe_stream_article(i))
    return JsonResponse(li,safe=False)

##用户公开的历史转发和动态
###方法 GET
###参数 无
@authorization_id
def user_history_public(request,id,p):
    user=Aurora_User_Model.objects.get(user_id=id)
    li=[]
    p=int(p)
    if Aurora_Article_Model.objects.filter(article_group=None,article_author=user).count()<p*20:
        return JsonResponse(li,safe=False)
    articles=Aurora_Article_Model.objects.filter(article_group=None,article_author=user)[p*20:(p+1)*20]
    for i in articles:
        li.append(Secondary.safe_stream_article(i))
    return JsonResponse(li,safe=False)

##用户公开的收藏夹Rect
###方法 GET
###参数 无
@authorization_id
def user_summary_rect_public(request,id):
    user=Aurora_User_Model.objects.get(user_id=id)
    me=Aurora_User_Model.objects.get(user_id=request.session['id'])
    li=[]
    if(Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=me,m2m_blocking=user).count()!=0):
        return response403("您已经被对方拉黑")
    summarys=Aurora_Summary_Model.objects.filter(summary_author=user,summary_type=constants.Summary_Type.Public)[:5] #取五个
    for i in summarys:
        li.append(Secondary.safe_summary_rect(i))
    return JsonResponse(li,safe=False)

###用户公开的收藏夹列表
###方法 GET
###参数 无
@authorization_id
def user_summary_public(request,id,p):
    user=Aurora_User_Model.objects.get(user_id=id)
    me=Aurora_User_Model.objects.get(user_id=request.session['id'])
    if(Aurora_M2M_User_User_Block_Model.objects.filter(m2m_be_blocked=me,m2m_blocking=user).count()!=0):
        return response403("您已经被对方拉黑")
    li=[]
    p=int(p)
    star_list=Aurora_Summary_Model.objects.filter(summary_author=user,summary_type=constants.Summary_Type.Public).order_by("summary_create_time")[20*p:20*(p+1)]
    for i in star_list:
        li.append(Secondary.safe_summary_meta(i))
    return JsonResponse(li,safe=False)

##用户关注的收藏夹
###方法 GET
###参数 无
@authorization_id
def user_following_summary(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    li=[]
    p=int(p)
    if Aurora_M2M_User_Follow_Summary_Model.objects.filter(m2m_user=user).count()<p*20:
        return JsonResponse(li,safe=False)
    summarys=Aurora_M2M_User_Follow_Summary_Model.objects.filter(m2m_user=user)[p*20:(p+1)*20]
    for i in summarys:
        li.append(Secondary.safe_summary_meta(i.m2m_summary))
    return JsonResponse(li,safe=False)

##用户关注的内容更新
###方法 GET
###参数 无
@authorization_id
def user_subscribe(request,p):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    li=[]
    p=int(p)
    query=Aurora_Article_Model.objects.filter(article_author__aurora_m2m_user_follow_summary_model__m2m_user=user) #关注的收藏夹的新帖子
    following_users=Aurora_M2M_User_User_Follow_Model.objects.filter(m2m_following=user) #获取用户的关注对象列表
    for i in following_users:
        m=Aurora_Article_Model.objects.filter(article_author__f_followed_user__m2m_be_followed=i.m2m_be_followed) #定义了related_name需要直接引这个
        query=(query|m) #合并结果集
    query=query.distinct().order_by("-article_create_time")[20*p:20*(p+1)]
    for i in query:
        li.append(Secondary.safe_stream_article(i))
    return JsonResponse(li,safe=False)

##文章置顶与取消置顶
###方法 GET
###参数 无
@authorization_id
def article_set_top(request,id):
    try:
        article=Aurora_Article_Model.objects.get(article_id=id)
    except:
        return response404("找不到这篇文章哦？")
    if article.article_sign%constants.Article_Sign.APP_Top<constants.Article_Sign.Group_Top:
        #非置顶
        article.article_sign+=constants.Article_Sign.Group_Top
        article.save()
        return HttpResponse("置顶成功！") 
    else:
        article.article_sign-=constants.Article_Sign.Group_Top
        article.save()
        return HttpResponse("取消置顶成功！") 

##版本检查
###方法 GET
###参数 version    
@parameter_verify("version",opt="GET")
def version_check(request):
    try:
        detail=Aurora_Version_Model.objects.get(version=request.GET['version'])
    except:
        return response404()
    newest=Aurora_Version_Model.objects.all().last()
    if newest.version==detail.version: #是最新版本
        return JsonResponse({'code':'200','version':''}) #200 无需更新
    higher=Aurora_Version_Model.objects.filter(time__gt=detail.time).order_by("-time") #比本版本新的版本
    for i in higher:
        if i.force==True:
            return JsonResponse({'code':'201','version':i.version}) #201 强制更新 
    return JsonResponse({'code':'202','version':newest.version}) #202 选择性更新

##用户协议
###方法 GET
###参数 无
def agreement(request):
    with open("C:\\Aurora_Backend\\file\\agreements\\用户协议.txt","r",encoding="utf8") as f:
        return HttpResponse(f.read())

##发送邀请邮件
###方法 POST
###参数 password email
@parameter_verify("password","email",opt="POST")
@authorization_id
def invite_submit_email(request):
    user=Aurora_User_Model.objects.get(user_id=request.session['id'])
    passwd=request.POST["password"]
    if not user.user_login_pwd==hashlib.md5((passwd+user.user_login_salt).encode(encoding="utf-8")).hexdigest():
        #先验证密码是不是对的
        return response403("密码错误") 
    stamp=timezone.now().timestamp()
    if stamp - user.user_date_create.timestamp() > 2626560 or user.digit_article>=10 :
        #满足要求
        #简单加密一下
        b64=base64.b64encode(request.POST['email'].encode('utf-8'))
        b64=b64[3:]+b64[0:3] #移位一下
        try:
            invitation=Aurora_Invitation.objects.create(remark="担保人："+str(user.user_id),mail=b64) #生成邀请码
        except:
            return response403("生成邀请码失败！这个邮箱可能已经被发送了邀请码！")
        try:
            EmailMultiAlternatives("Aurora破晓邀请码发送通知",
            "亲爱的用户，您好：\n您的邀请码为 {0} ，绑定邮箱为此邮箱，并且不能解绑。\n请您在以下链接中下载破晓APP（仅Android测试）\n {1} \n破晓社区诚待您的加入！\n破晓的Augustine".format(invitation.code,settings.DOMAIN+settings.APP_LATEST_DOWNLOAD),
            settings.EMAIL_HOST_USER,[request.POST['email']]).send()
            return HttpResponse("发送成功~感谢您对破晓社区的支持~")
        except Exception as e:
            return response404("发送失败！失败原因如下： {0}".format(e))
    else:
        return response403("您的加入时间不够1个月且发帖数量不足10")

        