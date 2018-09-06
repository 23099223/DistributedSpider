import json
import logging
import os
import socket
import socketserver
import sys
import threading

from mongo_redis_mgr import MongoRedisManager as mrmg

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.DEBUG)


class ServerSocket:
    def __init__(self, callback, mongo_redis, host='localhost', port=3028):
        print(host)
        print(port)
        self.ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = callback
        self.mongo_redis = mongo_redis
        try:
            print("bind ", port)
            self.ser_socket.bind((host, port))
        except socket.error as e:
            print(e)
            sys.exit(1)
        self.ser_socket.listen(10)
        self.kill_conn = "local"

    def receive_signal(self, signum, stack):
        self.kill_conn = self.mongo_redis.logout_client(flag=False)  # 会由数据库控制
        print(self.kill_conn)

    def startlistening(self):
        while True:
            print('Waiting for new connection ... ')
            conn, addr = self.ser_socket.accept()
            # _thread.start_new_thread(self.clientthread, (conn,))
            t = threading.Thread(target=self.clientthread, name='clientthread', args=(conn,))
            t.start()

    def deal_recv_data(self, conn):
        return json.loads(conn.recv(102400).decode('utf8'))

    def clientthread(self, conn):
        data = self.deal_recv_data(conn)
        client_id = data.get("client_id")
        logging.info("recv_data: %s" % data)
        if self.kill_conn == data.get("client_id"):
            conn.sendall(json.dumps({"signal": "done"}).encode("utf8"))
            self.kill_conn = "local"
        else:
            if data.get("signal") == "sign":
                if self.mongo_redis.sign_check_client(client_id):
                    conn.sendall(json.dumps({"client_id": client_id}).encode('utf8'))
                else:
                    conn.sendall(json.dumps({"erro": "1"}).encode('utf8'))
            elif data.get("signal") == "heart":
                pass
            elif data.get("signal") == "logout":
                pass
            else:
                if self.mongo_redis.sign_check_client(client_id, True):
                    conn.sendall(self.send_msg())
                else:
                    conn.sendall(json.dumps({"erro": "2"}).encode('utf8'))

        conn.close()

    # 需要改
    def send_msg(self):
        msg = json.dumps(self.mongo_redis.dequeue_url()).encode('utf8')

        return msg

    def start(self):
        t = threading.Thread(target=self.startlistening, name='startlistening', args=())
        t.start()
        # _thread.start_new_thread(self.startlistening, ())

    def close(self):
        # self.s.shutdown(socket.SHUT_WR)
        logging.info("exit")
        self.ser_socket.close()


def msg_received(data):
    ret = data.decode('utf8')
    return ret


class Master(socketserver.BaseRequestHandler):
    """服务端大脑:用于处理slave请求"""

    def setup(self):
        """
        在handle()方法之前调用setup(),完成一些初始化的工作:
        """
        pass

    def handle(self):
        """完成所有的对于每个请求的处理工作,也就是实现服务端的业务逻辑"""
        while True:
            data, spider_id, sig_type, slave_id, url_info, content, msg_code = deal_recv_data(self.request.recv(10240))
            if data is None or slave_id is None or sig_type is None:
                break
            elif mrmg().r_sismember("slave_id_set", slave_id) == 0 and sig_type != "login":
                break
            logout_flag = mrmg().r_sismember("slave_id_set", slave_id) == 0
            if sig_type == "login":
                # 注册
                mrmg().r_sadd("slave_id_set", slave_id)
                self.request.sendall(deal_send_data(data))
            elif sig_type == "spide":
                # 向slave发送爬取信息,且保存返回值

                self.request.sendall(deal_send_data(data))
            elif sig_type == "error":
                # 爬取失败,保存失败池中
                pass

    def finish(self):
        """在handle()方法之后调用,完成一些清理的工作,如果setup()抛异常侧不会调用"""
        pass


def deal_recv_data(data):
    # return json.loads(data, encoding="utf8")
    if not data:
        return None, None, None, None, None, None, None
    data = json.loads(data, encoding="utf8")
    print(data)
    return data, data.get("spider_id"), data.get("sig_type"), data.get("slave_id"), data.get("url_info"), data.get(
        "content"), data.get("msg_code")


def deal_send_data(data):
    return json.dumps(data).encode('utf8')


def save_ret(data: {}):
    """根据depth获取下一个depth或者确定是否是最后一个depth保存结果"""
    url_info = data.get("url_info")
    depth = url_info.get("depth")
    depth_list = mrmg().r_lrange("depth_list", 0, -1)
    length, dep_index = len(depth_list), depth_list.index(depth)
    if length == dep_index + 1:
        # 保存结果
        pass
    else:
        # 保存url
        next_depth = depth_list[dep_index + 1]
        url_list = data.get("content")

        pass


if __name__ == "__main__":
    # 注册信号处理程序
    logging.info("PID = %s" % os.getpid())
    # server = ServerSocket(msg_received, mrmg.MongoRedisManager(), host=sc.ser_ip, port=sc.ser_port)
    # signal.signal(signal.SIGUSR1, server.receive_signal)
    # server.start()
    # time.sleep(10)
    # 等待直到接收一个信号
    # signal.pause()
    # mrg = mrmg.MongoRedisManager()
    # print(mrg.r_get("test"))
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 3028,), Master)
    server.serve_forever()
