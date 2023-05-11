'''
Author: AugustTheodor
Date: 2022-01-07 15:10:05
LastEditors: AugustTheodor
LastEditTime: 2022-01-25 16:25:20
Description: 模型类二级引用，安全方法
'''
from asyncio.windows_events import NULL
import re
import hashlib
from aurora_etc import constants
from aurora_main.models import *

class Safe_Words(): #安全过滤类

    SAFE_SUFFIX=["jpg","jpeg","png","gif"]

    def safe_number_letter(id:str):
        if re.findall(r"([^a-zA-Z0-9])",id)!=[]: #捕获非数字字母的其他字符
            return None
        return id
    
    def safe_number_letter_special(keyword:str):
        if re.findall(r"([^（）()./\\|_@#$%&*\^?_\-a-zA-Z0-9])",keyword)!=[]:
            return None
        return keyword

    def safe_keyword(keyword:str): #安全关键词，只允许中英文数字英文逗号
        if re.findall(r"([^\u4e00-\u9fa5a-zA-Z0-9,])",keyword)!=[]:
            return None
        return keyword
    
    def safe_number_letter_chinese(keyword:str):
        if re.findall(r"([^./\\|_@#$%&*\^?_\-\u4e00-\u9fa5a-zA-Z0-9])",keyword)!=[]:
            return None
        return keyword

    def safe_link(link:str): #安全连接，指传回的str
        suffix=link.split(".") #后缀
        if not suffix[-1] in Safe_Words.SAFE_SUFFIX or len(suffix)>2:
            return False
        url=Safe_Words.safe_number_letter(suffix[0])
        if url!=False:
            return link
        else:
            return False
        
class Model_Secondary_Reference():   

#------------------------------------------------------------------------------------------------------------------------
# 以下是各个model的映射函数，输入一个QuerySet，返回一个经过删减的安全字典，这些删减使得字典中没有敏感参数
#------------------------------------------------------------------------------------------------------------------------

    def safe_user_meta(i): #pypy类rb，为什么不能来点yield代码
        #获取用户的详细信息，一次只能获取一个
        s={}
        s['user_name']=i.user_name
        s['user_himg']=i.himg
        s['user_bimg']=i.bimg
        s['user_signature']=i.user_signature
        s['user_following']=i.digit_following
        s['user_followed']=i.digit_followed
        s['user_article']=i.digit_article
        s['user_group']=i.digit_group
        s['summary_sum']=Aurora_Summary_Model.objects.filter(summary_author=i,summary_type=constants.Summary_Type.Public).count()
        return s

    def safe_stream_article(i):
        #获取推送中帖子的信息(推送里这几个适配前端所以需要相同的key)
        s={}
        s['title']=i.article_author.user_name
        if i.article_group==None:
            s['group_name']=None
            s['title']=i.article_author.user_name
        else:
            s['group_name']=i.article_group.group_title
        if i.article_origin==None:
            s['origin']=None
        else:
            s['origin']=i.article_origin.article_id
            s['origin_title']=i.article_origin.article_title
            s['origin_author_name']=i.article_origin.article_author.user_name
            s['origin_author_nick']=i.article_origin.article_author.himg
            s['origin_author_id']=i.article_origin.article_author.user_id
            s['title']=i.article_author.user_name
        if i.article_title=='':
            s['content']=i.article_content
        else:
            s['content']=i.article_title
        s['nick_img']=i.article_author.himg
        s['nick']=i.article_author.user_name
        s['s_id']=i.article_id
        s['img_list']=i.article_img_list
        return s

    def safe_group_article(i):
        #组内显示的帖子的信息
        s={}
        s['article_id']=i.article_id
        s['article_title']=i.article_title
        s['author_id']=i.article_author.user_id
        s['author_name']=i.article_author.user_name
        s['author_nick']=i.article_author.himg
        s['article_amount']=i.info.article_comment
        s['article_time']=i.article_create_time
        return s

    def safe_summary_article(i):
        #组内显示的帖子的信息
        s={}
        s['article_id']=i.m2m_article.article_id
        s['article_title']=i.m2m_article.article_title
        s['author_id']=i.m2m_article.article_author.user_id
        s['author_name']=i.m2m_article.article_author.user_name
        s['author_nick']=i.m2m_article.article_author.himg
        s['desc']=i.desc
        s['time']=i.time
        return s

    def safe_article_detail(i):
        #获取帖子的主楼
        s={}
        s['safe_type']=str(i.article_type) #类型
        s['title']=i.article_title
        s['content']=i.article_content
        s['image']=i.article_img_list
        if i.article_group!=None:
            s['group']=i.article_group.group_id #小组id
            s['group_name']=i.article_group.group_title
            s['group_nick']=i.article_group.group_img
        s['author']=i.article_author.user_id #作者id
        s['author_name']=i.article_author.user_name
        s['author_nick']=i.article_author.himg
        s['time']=i.article_create_time
        s['a_prefer']=i.info.article_prefer #点赞
        s['a_up']=i.info.article_up #顶
        s['a_transmit']=i.info.article_transmit #转发
        s['a_star']=i.info.article_star #收藏
        s['a_comment']=i.info.article_comment #评论
        return s

    def safe_comment(i):
        #获取一条回复的详细信息
        s={}
        s['author']=i.comment_author.user_id #作者id
        s['author_name']=i.comment_author.user_name
        s['author_nick']=i.comment_author.himg
        s['content']=i.comment_content
        s['id']=i.comment_id
        s['like']=i.prefer
        s['time']=i.comment_create_time
        s['image']=i.comment_img
        if(i.reply_comment!=None):
            #这条回复回复了另一条回复
            s['reply_comment_content']=i.reply_comment.comment_content
            s['reply_comment_author_name']=i.reply_comment.comment_author.user_name
        return s
    
    def safe_transmit(i):
        s={}
        s['author']=i.article_author.user_id 
        s['author_name']=i.article_author.user_name
        s['author_nick']=i.article_author.himg
        s['content']=i.article_content
        s['id']=i.article_id
        s['time']=i.article_create_time
        return s

    def safe_notice_notice(q):
        #获取通知
        li=[]
        for i in q:
            s={}
            s['content']=i.content
            s['time']=str(i.time)
            s['type']=i.type
            s['type_id']=i.type_id
            li.append(s)
        return str(li)

    def safe_notice_comment(q):
        #获取被评论通知
        li=[]
        for i in q:
            s={}
            s['author_name']=i.from_comment.comment_author.user_name
            s['author']=str(i.from_comment.comment_author.user_id)
            s['time']=str(i.from_comment.comment_create_time)
            s['content']=i.from_comment.comment_content
            s['reply_content']=""
            s['reply_title']=i.from_comment.comment_article.article_title
            s['trend_type']=i.type
            s['trend']=str(i.from_comment.comment_article.article_id)
            li.append(s)
        return str(li)

    def safe_notice_message(q):
        #获取私信
        li=[]
        for i in q:
            s={}
            s['author_id']=str(i.from_user.user_id)
            s['chat_id']=str(i.from_user.user_id) #当为私聊时，chatid为被私聊的人的id。
            s['content']=i.content
            s['img']=i.image
            s['time']=str(i.time)
            li.append(s)
        return str(li)

    def safe_group_item(i):
        #获取小组的部分信息，用于显示缩略图
        s={}
        s['group_id']=i.group_id
        s['group_name']=i.group_title
        s['group_pic']=i.group_img
        return s

    def safe_group_meta(i):
        #获取小组基本信息
        s={}
        s['group_name']=i.group_title
        s['group_pic']=i.group_img
        s['group_introduction']=i.group_introduction
        s['group_member']=i.group_member
        s['group_member_name']=i.group_member_name
        s['group_color']=i.group_color
        s['group_join_type']=i.group_join_type
        return s

    def safe_summary_meta(i):
        #获取收藏夹的小信息
        s={}
        s["summary_link"]=i.summary_id
        s["summary_name"]=i.summary_title
        s["summary_desc"]=i.summary_describe
        s["summary_pic"]=i.summary_pic
        return s
    
    def safe_summary_rect(i):
        #获取收藏夹的Rect
        s={}
        s["summary_name"]=i.summary_title
        s["summary_pic"]=i.summary_pic
        s["summary_id"]=i.summary_id
        s["summary_sum"]=Aurora_Summary_Info_Model.objects.get(comb=i).summary_dict
        return s
    
    def safe_summary_detail(i):
        s={}
        s["summary_link"]=i.summary_id
        s["summary_name"]=i.summary_title
        s["summary_desc"]=i.summary_describe
        s["summary_pic"]=i.summary_pic
        info=Aurora_Summary_Info_Model.objects.get(comb=i)
        s["summary_dict"]=info.summary_dict
        s["summary_follow"]=info.summary_follow
        return s
    
    def safe_report_article(i): #只做文章举报
        s={}
        s['report_content']=i.article_title
        s['article_id']=i.article_id
        s['report_time']=i.info.article_report #被举报次数
        return s

    def safe_report_log(i):
        s={}
        s['report_content']=Model_Secondary_Reference.report_find_content_by_type_id(i)
        if s['report_content']==None:
            i.delete()
            return None #若没有就是已删除，不整
        s['id']=i.comb #举报的ID直接使用了comb
        s['type']=i.with_type
        s['content_id']=i.with_id
        s['report_reason']=[k for k,v in constants.Report_Reason.reason if v==i.with_reason]
        s['report_time']=str(i.time)
        return s

    def safe_member_meta(i):
        s={}
        s['member_name']=i.user_name
        s['member_id']=i.user_id
        s['member_nick']=i.himg
        return s
    
    def safe_admin_log(i):
        s={}
        s['content']=i.content
        s['operation']=i.operation
        s['admin']=i.admin_user.user_name
        s['time']=i.time
        return s

    def safe_group_list(i):
        s={}
        s['group_pic']=i.group_img
        s['group_name']=i.group_title
        s['group_desc']=i.group_introduction
        s['group_number']=i.group_member
        s['group_id']=i.group_id
        return s
    
    def safe_admin_apply(i):
        s={}
        s['user_name']=i.m2m_user.user_name
        s['user_nick']=i.m2m_user.himg
        s['content']=i.content
        s['id']=i.comb
        return s

    def report_find_content_by_type_id(i:Aurora_M2M_Report_Log_Model):
        #根据type 和 id 找原文
        if i.with_type==constants.Type.Article:
            try:
                return Aurora_Article_Model.objects.get(article_id=i.with_id).article_title
            except:
                return None
        if i.with_type==constants.Type.Group:
            try:
                return Aurora_Group_Model.objects.get(group_id=i.with_id).group_title
            except:
                return None
        if i.with_type==constants.Type.Comment:
            try:
                return Aurora_Article_Comment_Model.objects.get(comment_id=i.with_id).comment_content
            except:    
                return None
        return None

    def report_find_thing_by_type_id(i:Aurora_M2M_Report_Log_Model):
        if i.with_type==constants.Type.Article:
            try:
                return Aurora_Article_Model.objects.get(article_id=i.with_id)
            except:
                return None
        if i.with_type==constants.Type.Group:
            try:
                return Aurora_Group_Model.objects.get(group_id=i.with_id)
            except:
                return None
        if i.with_type==constants.Type.Comment:
            try:
                return Aurora_Article_Comment_Model.objects.get(comment_id=i.with_id)
            except:    
                return None
        return None
    
    def report_find_author_by_type_id(i:Aurora_M2M_Report_Log_Model):
        if i.with_type==constants.Type.Article:
            try:
                return Aurora_Article_Model.objects.get(article_id=i.with_id).article_author
            except:
                return None
        if i.with_type==constants.Type.Group:
                return None
        if i.with_type==constants.Type.Comment:
            try:
                return Aurora_Article_Comment_Model.objects.get(comment_id=i.with_id).comment_author
            except:    
                return None
        return None

#------------------------------------------------------------------------------------------------------------------------
# 以下函数封装一些与model相关的功能，使用这些功能必须通过这些函数，因为它们会顺便维护数据库中的逻辑关系（总数与M2M表记录）
#------------------------------------------------------------------------------------------------------------------------
    def add_summary(user,name:str,desc:str,pic:str,type:str):
        pic=Safe_Words.safe_link(pic)
        summary=Aurora_Summary_Model.objects.create(summary_author=user,summary_title=name,summary_pic=pic,summary_describe=desc,summary_type=int(type))
        Aurora_Summary_Info_Model.objects.create(comb=summary)
        return summary.summary_id

    def add_article(title:str,content:str,image:str,author,group:str,type:int): #创建帖子及其数据类
        try: #因为get要返回一个，如果是空或者多就会报错，而他理论上只会返回一个
            author.digit_article+=1
            author.save()
            article=Aurora_Article_Model.objects.create(article_type=type,article_title=title,article_content=content,article_author=author,article_group=group,article_img_list=image)
            Aurora_Article_Info_Model.objects.create(comb=article)
            return article.article_id 
        except:
            return False
    
    def add_article_comment(content:str,authorID:str,articleID:str,type:str): #创建回复
        try:
            article=Aurora_Article_Model.objects.get(article_id=articleID)
            author=Aurora_User_Model.objects.get(user_id=authorID)
            article_info=Aurora_Article_Info_Model.objects.get(comb=article)
        except:
            return False
        comment=Aurora_Article_Comment_Model.objects.create(comment_author=author,comment_article=article,comment_content=content)
        Aurora_Temp_M2M_Comment_Notice_Model.objects.create(to_user=article.article_author,from_comment=comment,type=type)
        article_info.article_comment+=1
        article_info.save() #摘要也要更新
        return comment.comment_id #返回id

    def add_group(title:str,keyword:str):
        pass #暂时还是不要开放小组申请，由官方添加
