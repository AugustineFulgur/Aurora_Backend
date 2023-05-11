'''
Author: AugustTheodor
Date: 2022-01-04 14:38:53
LastEditors: AugustTheodor
LastEditTime: 2022-01-07 15:51:35
Description: 主键的COMB类型
'''

import uuid
import time

#COMB主键的简单实现
class Aurora_Comb_UUID:
    def CombID():
        top20=str(uuid.uuid1()).replace("-","")[:-12] #前二十位（10bit）
        last12=str(time.time()).replace(".","")[-12:] #后十二位 （6bit）
        return top20+last12

