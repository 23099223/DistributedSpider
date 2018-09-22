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
            data = self.deal_send_data(data, sig_type)
            if data is None:
                break
            self.request.sendall(json.dumps(data).encode('utf8'))

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
        if self.mrmg.r_sismember("logout_set", data.get("slave_id")) != 0:
            data["sig_type"] = "logout"
            return data
        if sig_type == "login":
            slave_id = data.get("slave_id")
            self.mrmg.r_sadd("slave_id_set", slave_id)
            data["msg"] = "success"
            pass
        elif sig_type == "spide":
            if data.get("sig_type") == "spide" and data.get("url_info") is not None:
                self.save_ret(data)
                # 将已爬取过的url从running池中删除
                self.mrmg.r_hdel("running_map", data.get("url_info").get("url"))
            ###### 应该是原子的
            url_info = self.mrmg.r_lpop(data.get("spider_id") + "_list")
            if url_info is None and self.mrmg.r_exists("running_map") != 1:
                data["sig_type"] = "exit"
            elif url_info is None:
                data["sig_type"] = "wait"
                data["url_info"] = url_info
            else:
                url_info = eval(url_info)
                data["url_info"] = url_info
                # 将获取的url保存到running池中
                self.mrmg.r_hset("running_map", url_info.get("url"), url_info.get("depth"))
            ######
        elif sig_type == "error":
            error_dcit = data.get("url_info")
            error_dcit["msg"] = data.get("ret_msg")
            self.mrmg.r_lpush("error_list", error_dcit)
            data = self.deal_send_data(data, "spide")
        else:
            return None
        return data

    def save_ret(self, data: {}):
        """根据depth获取下一个depth或者确定是否是最后一个depth保存结果"""
        url_info = data.get("url_info")
        if url_info is None:
            return
        depth = url_info.get("depth")
        depth_list = self.mrmg.r_lrange(data.get("spider_id") + "_depth_list", 0, -1)
        length, dep_index = len(depth_list), depth_list.index(depth)
        if length == dep_index + 1:
            # 保存结果
            self.mrmg.r_rpush("ret_list", *data.get("content"))
        else:
            # 保存url
            next_depth = depth_list[dep_index + 1]
            url_list = data.get("content")
            spider_list = [{"depth": next_depth, "url": url} for url in url_list]
            print("spider_list:>", spider_list)
            self.mrmg.r_rpush(data.get("spider_id") + "_list", *spider_list)


if __name__ == "__main__":
    # 注册信号处理程序
    logging.info("PID = %s" % os.getpid())
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 9320,), Master)
    server.serve_forever()
