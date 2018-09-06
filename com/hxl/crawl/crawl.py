import logging
import sys
from time import sleep

import requests
import urllib3
from lxml import etree
from requests.exceptions import ReadTimeout

import crawl_config as cc
import socket_config as sc
from socket_client import SocketClient

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.DEBUG)
urllib3.disable_warnings()


def get_page_content(cur_url: str, depth: str, encoding="utf-8") -> list:
    try:
        response = requests.get(cur_url, headers=cc.get_request_headers(), verify=False, timeout=5)
        response.encoding = encoding
        content = response.text
    except ReadTimeout:
        logging.error("%s: 请求超时" % cur_url)
    except requests.ConnectionError:
        logging.error("%s: ConnectionError" % cur_url)
    except requests.RequestException as err:
        logging.error("%s: %s" % (cur_url, str(err)))
    finally:
        if response.status_code == "200":
            ret_from_page = cc.get_depth_result(etree.HTML(content), depth)
            return ret_from_page
        else:
            return ["error"]


# 初始传入注册的id号
def init(clid: str):
    global client_socket
    global client_id
    client_socket = SocketClient(sc.ser_ip, sc.ser_port)
    # sign in
    recv_msg_1 = client_socket.send({"signal": "sign", "client_id": clid})
    if recv_msg_1.get("client_id"):
        client_id = recv_msg_1.get("client_id")
        logging.info("client_id: %s" % client_id)
    else:
        sys.exit(recv_msg_1.get("erro"))
    logging.info("client_id = %s" % client_id)


init("test1")
recv_msg = client_socket.send({"client_id": client_id})
if recv_msg.get("signal") == "done":
    sys.exit(1)

while True:
    # recv_msg = client_socket.send({"client_id": client_id})
    result = get_page_content(recv_msg.get("url"), recv_msg.get("depth"), encoding="gbk")
    recv_msg = client_socket.send({"client_id": client_id, "signal": "crawl", "result": result})
    if recv_msg.get("signal") == "done":
        logging.info("server kill me, signal is %s" % recv_msg.get("signal"))
        sys.exit(1)
    logging.info("recv_msg is %s" % recv_msg)
    sleep(1)

    # if __name__ == "__main__":
    # print(cc.get_depth_xpath("depth_1"))
    # print(get_page_content("http://www.mafengwo.cn", "depth_2"))
