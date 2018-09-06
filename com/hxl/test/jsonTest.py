import os
import json

msg = {"sig_type": "login", "url": "www.baidu.com", "pid":str(os.getpid())}
print(msg.get("dwadwa"))
print(json.dumps(msg).encode('utf8'))
tt = json.dumps(msg)
print(tt)
print(json.loads(tt,encoding="utf8"))
# test = str(msg, encoding = "utf-8")
# print(test)
# ttt = eval(test)
# print(ttt)
if not b'':
    print("dawd")
else:
    print("dawdwa")
