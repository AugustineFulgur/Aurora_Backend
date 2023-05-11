#获取新邀请码并存储在指定文件中

from aurora_main.models import *
def run():
    num=int(input("请输入生成的数量："))
    txt=input("请输入保存的文件名")
    remark=input("请输入备注")
    with open("codes/"+txt,"w") as f: #保存在codes文件夹下
        for i in range(num):
            v=Aurora_Invitation.objects.create(remark=remark)
            f.writelines(str(v.code))  
    print("生成完毕。")