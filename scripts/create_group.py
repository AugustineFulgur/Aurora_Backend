#输入用户id和小组名，创建小组
from aurora_main.models import *
def run():
    id=input("请输入用户id:")
    name=input("请输入小组名：")
    try:
        user=Aurora_User_Model.objects.get(user_id=id)
    except:
        print("找不到这个用户。")
    group=Aurora_Group_Model.objects.create(group_title=name)
    Aurora_M2M_Group_Admin_User_Model.objects.create(with_group=group,admin_user=user,admin_type=constants.Admin_Type.Master)
    Aurora_M2M_User_Group_Model.objects.create(m2m_user=user,m2m_group=group)
    user.digit_group+=1
    user.save()
    group.group_member+=1
    group.save()
    Aurora_Temp_M2M_Notice_Model.objects.create(to_user=user,content="您的分组 {0} 创建成功！".format(name),type_id=group.group_id,type=constants.Type.Group)
    #发消息给创建的人
    print("创建成功！")
