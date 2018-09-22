# response = requests.get("https://www.taobao.com")
# print(type(response.text))


import json
import logging
import os
import socket
import time

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.DEBUG)
client = socket.socket()  # 定义协议类型,相当于生命socket类型,同时生成socket连接对象
client.connect(('127.0.0.1', 9320))
n = 100
msg = {"sig_type": "login", "spider_id": "test_no_a", "slave_id": "slave_1", "url_info": None, "pid": str(os.getpid())}
while n:
    client.send(json.dumps(msg).encode('utf8'))
    data = client.recv(10240)  # 这里是字节1k
    data = json.loads(data, encoding="utf8")
    print("recv:>", data)
    if data.get("sig_type") == "login" and data.get("msg") == "success":
        data["sig_type"] = "spide"
    elif data.get("sig_type") == "spide":
        data["content"] = ["url2", "url2", "url3"]
    elif data.get("sig_type") == "wait":
        data["sig_type"] = "spide"
        logging.info("收到wait信号,等待10秒")
        time.sleep(10)
    elif data.get("sig_type") == "exit":
        logging.info("收到exit信号,退出")
        break
    elif data.get("sig_type") == "logout":
        logging.info("收到logout信号,退出")
        break
    msg = data
    print("msg:>", msg)
    n = n - 1
    time.sleep(1)
time.sleep(1)
client.close()
