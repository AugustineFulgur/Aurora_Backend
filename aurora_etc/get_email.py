import base64

email=input("请输入邮箱：")
b64=base64.b64encode(email.encode('utf-8'))
b64=b64[3:]+b64[0:3] #移位一下
print(b64)