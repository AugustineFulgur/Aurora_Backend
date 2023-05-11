# 更新版本

from aurora_main.models import *

def run():
    x=input("请输入要更新的版本：")
    y=input("请问这是否是强制更新？（Y）")=="Y"
    Aurora_Version_Model.objects.create(version=x,force=y)