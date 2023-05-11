
class Report_Reason():
    #小组自定义的举报理由不能超过10个
    #APP范围内的理由以1000开头
    reason={
        "辱女词汇或对全体女性的攻击":1001,
        "认为作者是男性":1002,
        "语言不友善":1003,
        "广告、恶意引流":1004,
        "政治相关":1005,
        "引战言论、钓鱼":1006,
        "违法违规言论":1007,
        "抄袭、侵犯他人权益（若您为当事人，请发邮件）":1008,
    }

class Summary_Type():
    Public=0
    Private=1

class Type():
    Group="分组"
    Article="帖子"
    User="用户"
    Comment="评论"
    Transmit="转发"
    Trend="动态"

class Admin_Type():
    Admin="管理员"
    Master="组长"

class Article_Sign():
    Normal=0
    Group_Elite=10 #精华
    Group_Top=100
    APP_Top=1000

class Admin_Log_Operator():
    #管理操作
    Delete="删除"
    Modify="修改"
    Block="封禁"
    Remove="移出"
    Approval="批准"
    Upgrade="升职"

class Group_Join_Type():
    #小组加入方式
    No_Condition=1 #无条件加入
    Followed=2 #被关注数
    Apply=3 #申请加入
    Answer=4 #口令

class Report_Deal_Type():
    #投诉的处理方式
    Kick_Out="K" #移出
    Ban="B" #封禁
    Delete="D" #删除
    Nothing="N" #不处理