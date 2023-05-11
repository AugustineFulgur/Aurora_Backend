import hashlib

password=input("输入明文密码：")
salt="" #盐，我还没想好选啥
md5=hashlib.md5()
md5.update((password+salt).encode(encoding="utf8"))
print(md5.hexdigest())