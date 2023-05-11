'''
Author: AugustTheodor
Date: 2022-01-17 10:59:40
LastEditors: AugustTheodor
LastEditTime: 2022-01-19 10:15:30
Description: 丢一些垃圾
'''

from django.http import JsonResponse
from django.http import HttpResponse

#在写个人博客期间造的轮子（甚至不配叫轮子），想不到还有用到的一天啊- -
#这个函数将Django Model查询的结果集转换为list，然后进一步返回一个JsonResponse
def query2json(**kwargs):
    list_query={}
    for key,value in kwargs:
        list_query.update({key,value.values()})
    return JsonResponse(list_query,safe=False)

def str2list(s:str): #没有双引号的str转为list
    listr=[]
    s=s[1:-1] #掐头去尾
    for i in s.split(","):
        listr.append(i)
    return listr

def response403(content="访问被拒绝"):
    return HttpResponse(status=403,content=content)

def response404(content=""):
    return HttpResponse(status=404,content=content) #pypy类rb时间到