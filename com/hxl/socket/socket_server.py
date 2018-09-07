import json
import logging
import os
import socketserver

from mongo_redis_mgr import MongoRedisManager

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.DEBUG)


class Master(socketserver.BaseRequestHandler):
    """服务端大脑:用于处理slave请求"""

    def __init__(self, request, client_address: (), threadingTCPServer):
        self.mrmg = MongoRedisManager()
        self.logout_flag = False
        self.request = request
        self.client_address = client_address
        self.server = threadingTCPServer
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        """
        在handle()方法之前调用setup(),完成一些初始化的工作:
        """
        pass

    def handle(self):
        """完成所有的对于每个请求的处理工作,也就是实现服务端的业务逻辑"""
        while True:
            data, spider_id, sig_type, slave_id, url_info, content, msg_code = self.deal_recv_data(
                self.request.recv(10240))
            if data is None or slave_id is None or sig_type is None:
                break
            elif self.mrmg.r_sismember("slave_id_set", slave_id) == 0 and sig_type != "login":
                break
            self.request.sendall(json.dumps(self.deal_send_data(data, sig_type)).encode('utf8'))

    def finish(self):
        """在handle()方法之后调用,完成一些清理的工作,如果setup()抛异常侧不会调用"""
        pass

    def deal_recv_data(self, data):
        """接收返回信息,将dict拆开"""
        if not data:
            return None, None, None, None, None, None, None
        data = json.loads(data, encoding="utf8")
        print(data)
        return data, data.get("spider_id"), data.get("sig_type"), data.get("slave_id"), data.get("url_info"), data.get(
            "content"), data.get("msg_code")

    def deal_send_data(self, data: {}, sig_type: str):
        """处理发送信息"""
        if sig_type == "login":
            slave_id = data.get("slave_id")
            self.mrmg.r_sadd("slave_id_set", slave_id)
            data["msg"] = "success"
            pass
        elif sig_type == "spide":
            if data.get("sig_type") == "spide":
                self.save_ret(data)
            url_info = self.mrmg.r_lpop(data.get("spider_id") + "_list")
            if url_info is None:
                data["sig_type"] = "wait"
            else:
                data["url_info"] = url_info
        elif sig_type == "error":
            error_dcit = data.get("url_info")
            error_dcit["msg"] = data.get("ret_msg")
            self.mrmg.r_lpush("error_list", error_dcit)
            data = self.deal_send_data(data, "spide")
        return data

    def save_ret(self, data: {}):
        """根据depth获取下一个depth或者确定是否是最后一个depth保存结果"""
        url_info = data.get("url_info")
        depth = url_info.get("depth")
        depth_list = self.mrmg.r_lrange("depth_list", 0, -1)
        length, dep_index = len(depth_list), depth_list.index(depth)
        if length == dep_index + 1:
            # 保存结果
            self.mrmg.r_lpush("ret_list", data.get("content"))
        else:
            # 保存url
            next_depth = depth_list[dep_index + 1]
            url_list = data.get("content")
            spider_list = [{"depth": next_depth, "url": url} for url in url_list]
            self.mrmg.r_lpush(data.get("spider_id") + "_list", *spider_list)


if __name__ == "__main__":
    # 注册信号处理程序
    logging.info("PID = %s" % os.getpid())
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 3028,), Master)
    server.serve_forever()
