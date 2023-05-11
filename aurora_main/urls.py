'''
Author: AugustTheodor
Date: 2021-12-09 16:19:31
LastEditors: AugustTheodor
LastEditTime: 2022-01-25 15:46:20
Description: Aurora_Backend
'''
from django.urls import path
from aurora_main import views as view

urlpatterns = [
    #path('heartbeat/',view.heartbeat),
    path('login/',view.login),
    path('register/',view.register),
    path('stream/square/',view.stream_square),
    path('agreement/',view.agreement), #返回用户协议
    #APP
    path('version/check/',view.version_check), #版本检查
    path('app/top/',view.app_top_articles), #获取置顶文章
    path('app/group/rank/',view.app_group_rank), #获取小组排名
    path('app/search/article/p/<p>',view.search_article), #搜索文章
    path('app/search/group/p/<p>',view.search_group), #搜索小组
    path('invite/submit/email/',view.invite_submit_email), #添加发送邀请码功能
    #文章部分
    path('article/<id>',view.article_detail),
    path('article/<id>/delete/',view.delete_article), #删除
    path('article/<id>/p/<p>',view.article_comment),
    path('article/<id>/up/',view.up_article),
    path('article/<id>/transmit/p/<p>',view.article_transmit), 
    path('article/<id>/set/comment/',view.article_set_comment), #回复
    path('article/<id>/set/transmit/',view.article_set_transmit), #转发
    path('article/<id>/set/like/',view.article_set_like), #点赞
    path('article/<id>/rect/',view.article_rect), #获取转发origin的rect
    path('article/<id>/top/',view.article_set_top), #管理员置顶文章
    #回复部分
    path('comment/<id>/set/like/',view.comment_set_like), #评论点赞
    path('comment/<id>/delete/',view.comment_delete), #评论删除
    #小组部分
    path('group/<id>',view.group_meta),
    path('group/<id>/fresh/<p>',view.group_fresh_article), #最新更新的帖子
    path('group/<id>/hot/<p>',view.group_hot_article), #更新最热的帖子
    path('group/<id>/follow/',view.group_follow), #关注
    path('group/<id>/set/article/',view.create_article), #创建文章
    path('group/<id>/top/',view.group_top_articles), #获取置顶
    path('group/<id>/admin/master/',view.group_admin_master), #获取组长 （单URL means of 尊贵 - -
    #小组管理
    path('group/report/deal/<report_id>/',view.group_deal_report), #处理投诉（删除记录的同时移出发帖人、移除帖子等）
    path('group/<id>/report/article/p/<p>',view.group_report_article), #按热度查看投诉
    path('group/<id>/report/log/p/<p>',view.group_report_log), #获取投诉列表
    path('group/<id>/admin/member/p/<p>',view.group_admin_member), #获取管理员列表
    path('group/<id>/admin/search/p/<p>',view.group_admin_search), #搜索成员
    path('group/<id>/admin/manage/member/<user_id>/',view.group_admin_manage_member), #管理人员（升为管理员、转让组长、移出分组，加入黑名单）
    path('group/<id>/admin/block/member/p/<p>',view.group_admin_block_member), #查看小组黑名单
    path('group/<id>/admin/manage/join/type/',view.admin_join_type), #(POST)修改入组方式 (GET)展示入组方式
    path('group/<id>/admin/log/p/<p>',view.admin_group_log), #查看管理日志
    path('group/<id>/modify/',view.modify_group_data), #修改小组信息
    path('group/<id>/admin/apply/p/<p>',view.admin_group_apply), #查看申请信息
    path('group/<id>/dismiss/',view.admin_dismiss), #辞职
    path('group/<group_id>/admin/apply/<apply_id>/deal/<method>/',view.admin_deal_apply), #处理申请
    #上传与下载
    path('upload/image/',view.upload_image),
    #用户部分
    path('user/<id>',view.user_detail),
    path('user/<id>/follow/',view.user_follow_user),
    path('user/<id>/block/',view.user_block_user),
    path('user/<id>/history/public/p/<p>',view.user_history_public), #用户公开的历史记录
    path('user/<id>/summary/public/rect/',view.user_summary_rect_public), #用户公开的列表Rect
    path('user/<id>/summary/public/p/<p>',view.user_summary_public), #用户公开的列表
    path('user/modify/',view.modify_user_data), #修改个人信息
    path('user/follow/group',view.user_follow_group), #获取用户关注的小组
    path('user/detail/follow/group/<p>',view.user_detail_follow_group), #列表版用户关注的小组
    path('user/following/people/<p>',view.user_following_user), #关注列表
    path('user/followed/people/<p>',view.user_followed_user), #粉丝列表
    path('user/subscribe/p/<p>',view.user_subscribe), #查看关注动态
    path('user/set/trend/',view.create_trend), #发布动态
    path('user/history/article/p/<p>',view.user_history_article), #查看自己发过的帖子
    #收藏（精选集）
    path('user/summary/list/p/<p>',view.user_summary_list), #查看自己的收藏夹
    path('user/following/summary/p/<p>',view.user_following_summary), #查看用户关注的收藏夹
    path('user/following/summary/list/p/<p>',view.user_following_summary_list),
    path('set/summary/',view.create_summary), #创建新的收藏夹
    path('summary/<summary_id>/add/<article_id>/',view.add_article_to_summary), #给收藏夹增加内容
    path('summary/<id>/',view.summary_meta), #获取收藏夹详细页面的信息
    path('summary/<id>/p/<p>',view.summary_detail), #获取收藏夹中的文章（分页）
    path('summary/<id>/modify/',view.modify_summary_data), #修改收藏夹信息
    path('summary/<id>/delete/',view.delete_summary), #删除收藏夹
    path('summary/<id>/follow/',view.summary_follow), #关注、取关收藏夹
    path('summary/<summary_id>/article/<article_id>/modify/',view.summary_article_desc_modify), #收藏夹收藏的帖子（也可以是其他东西）的收藏理由修改
    path('summary/<summary_id>/article/<article_id>/delete/',view.summary_article_delete), #删除收藏夹中收藏的帖子
    #私聊
    path('chat/<id>/',view.set_message),
    #举报
    path('report/<type>/<id>/reasons/',view.report_reasons), #获取举报理由
    path('report/<type>/<id>/submit/',view.report_submit), #提交举报
    #短请求
    path('short/user/<id>',view.short_user), #获取用户头像和昵称
    path('short/group/<id>',view.short_group), #获取小组的头像和名字
    #path('',),
]
