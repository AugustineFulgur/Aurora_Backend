import threading
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from aurora_main.models import *
from aurora_etc.model_secondary_reference import Model_Secondary_Reference as Secondary
import json,time

class ChatConsumer(WebsocketConsumer):
    
    def do_db(self):
        message=Aurora_Temp_M2M_Message_Model.objects.filter(to_user=self.user)
        comment=Aurora_Temp_M2M_Comment_Notice_Model.objects.filter(to_user=self.user)
        notice=Aurora_Temp_M2M_Notice_Model.objects.filter(to_user=self.user)
        if comment.count()+message.count()+notice.count()!=0: #有一条以上的新消息
            js={"message":Secondary.safe_notice_message(message),
                "comment":Secondary.safe_notice_comment(comment),
                "notice":Secondary.safe_notice_notice(notice),
            }
            message.delete()
            notice.delete()
            comment.delete()
            return js
        else:
            return None

    def connect(self):
        self.user= Aurora_User_Model.objects.get(user_id=self.scope["session"]["id"])
        if self.user!=None:
            self.accept()
        else:
            self.disconnect()

    def receive(self, text_data):
        if text_data=="HEARTBEAT":
            result=self.do_db()
            if result !=None: #查询有无新数据
                self.send(text_data=str(result))

    def disconnect(self, event):
        pass
