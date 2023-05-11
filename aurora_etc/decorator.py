'''
Author: AugustTheodor
Date: 2022-01-15 17:08:45
LastEditors: AugustTheodor
LastEditTime: 2022-01-25 16:43:24
Description: 一些装饰器
'''


from email.utils import decode_rfc2231
from http.client import HTTPResponse
from aurora_etc.etcs import *
from quopri import decodestring
from aurora_etc.model_secondary_reference import Model_Secondary_Reference as Secondary

##鉴权函数，确保请求端带有登陆权限
### request 请求
def authorization_id(func): 
    def decorate(request,**kwargs): #结果url里的参数作为字典传进来，所以写*args会报错啊- -
        if(request.session==None):
            return response403()
        if(not 'id' in request.session):
            return response403()
        return func(request,**kwargs)
    return decorate

##鉴定是否含有特定参数
### request 请求 一个指名参数opt为方法，可变参数为校验的参数列表
def parameter_verify(*args,**kwargs):
    def decorator(func):
        def decorate(request,**k):
            if(kwargs['opt']=='GET'):
                for i in args:
                    if(not i in request.GET):
                        return response403()
                    if(request.GET[i]==None):
                        return response403()
                return func(request,**k)
            elif(kwargs['opt']=='POST'):
                for i in args:
                    if(not i in request.POST):
                        return response403("请求的参数不完整")
                return func(request,**k)
            else:
                return response404("不存在的请求")
        return decorate
    return decorator

##特定参数是否为空
### request 请求 一个指名参数opt为方法，可变参数为校验的参数列表
def char_verify(*args,**kwargs):
    def decorator(func):
        def decorate(request,**k):
            if(kwargs['opt']=='GET'):
                for i in args:
                    if(request.GET[i]=="" or request.GET[i].isspace()):
                        return response403()
                return func(request,**k)
            elif(kwargs['opt']=='POST'):
                for i in args:
                    if(request.POST[i]=="" or request.POST[i].isspace()):
                        return response403("请填写必要项！")
                return func(request,**k)
            else:
                return response404("不存在的请求")
        return decorate
    return decorator

##给所有返回id或者False的函数使用，当返回False时返回404，id则包装为JsonResponse
def decorate_ids(func):
    def decorate(request,**k):
        rid=func(request,**k)
        if rid==False:
            return response404("创建失败！")
        else:
            return JsonResponse({'rid':rid})
    return decorate
    






