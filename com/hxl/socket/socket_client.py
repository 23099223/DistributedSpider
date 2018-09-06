import json
import logging
import socket
import sys
import time

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.DEBUG)


class SocketClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None

    def send(self, message) -> {}:
        try:
            # Create a TCP/IP socket
            logging.info("connecting to %s" % self.server_port)
            self.sock = socket.create_connection((self.server_ip, self.server_port))
            # Send data
            logging.info('connected! client sends %s' % json.loads(json.dumps(message)))
            self.sock.sendall(json.dumps(message).encode('utf8'))

            data = self.deal_recv_data()

            return data
        except Exception as err:
            # Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            logging.error('Get Error Message: %s' % err)
            return {}
        finally:
            pass
            # if hasattr(self, 'sock'):
            #     self.sock.close()

    def deal_recv_data(self) -> {}:
        return json.loads(self.sock.recv(10240).decode('utf8'))


if __name__ == '__main__':
    client = SocketClient('localhost', 3028)
    recv_msg = client.send("hah")
    logging.info(recv_msg)
    if recv_msg.get("signal") == "done":
        sys.exit(1)
    while True:
        # result = crawl.get_page_content(recv_msg, "depth_2")
        recv_msg = client.send("ddd")
        if recv_msg.get("signal") == "done":
            sys.exit(1)
        print(recv_msg)
        time.sleep(1)
