# response = requests.get("https://www.taobao.com")
# print(type(response.text))


import json
import os
# 客户端
import socket
import time

client = socket.socket()  # 定义协议类型,相当于生命socket类型,同时生成socket连接对象
client.connect(('127.0.0.1', 3028))
n = 10
while n:
    msg = {"sig_type": "login", "slave_id": "slave_3", "url": "www.baidu.com", "pid": str(os.getpid())}
    client.send(json.dumps(msg).encode('utf8'))
    data = client.recv(10240)  # 这里是字节1k
    data = json.loads(data, encoding="utf8")
    print("recv:>", data)
    n = n - 1
    time.sleep(1)
time.sleep(1)
client.close()
