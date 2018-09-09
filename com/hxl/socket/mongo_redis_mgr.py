from pymongo import MongoClient
from rediscluster import StrictRedisCluster

import config


class MongoRedisManager:
    def __init__(self, server_ip: str = "localhost", client=None):
        self.client = MongoClient(server_ip, 27017) if client is None else client
        # self.redis_client: redis.StrictRedis = redis.StrictRedis(host=server_ip, port=6379, db=0, decode_responses=True)
        self.redis_client = StrictRedisCluster(startup_nodes=config.startup_nodes, password="Redis@123!",
                                               decode_responses=True)
        self.db = self.client.spider

        # create index if db is empty
        if self.db.crawl.count() is 0:
            self.db.crawl.create_index('status')

    def sign_check_client(self, client_id: str, flag: bool = False) -> bool:
        """客户端的注册与检查 flag: False 注册, True 检查是否注册"""
        isSign = self.redis_client.sismember("client_id_set", client_id)
        if flag:
            return isSign
        else:
            if isSign:
                return False
            else:
                self.redis_client.sadd("client_id_set", client_id)
                return True

    def logout_client(self, client_id: str = "", flag: bool = True):
        """注销客户端 flag: True 注销 , False 待注销"""
        if flag:
            num = self.redis_client.srem("client_id_set", client_id)
            return num
        else:
            logout_client = self.redis_client.lpop("logout_list")
            return logout_client

    def insert_info_m(self, data):
        """添加url到mongoDB"""
        self.db.crawl.insert(data)

    def dequeue_url_m(self) -> dict:
        """从mongoDB中获取url 需要改:取批量url并更新为running,返回结果后更新为done"""
        record: dict = self.db.crawl.find_one_and_update(
            {'status': 'ready'},
            {'$set': {'status': 'running'}},
            {'upsert': False, 'returnNewDocument': False}
        )
        if record:
            return record
        else:
            return {}

    def r_lpush(self, key: str, *info):
        """list:向redis插入信息"""
        self.redis_client.lpush(key, *info)

    def r_get(self, key: str) -> str:
        """str:根据key获取信息"""
        ret = self.redis_client.get(key)
        return ret

    def r_lpop(self, key: str):
        """list:从左删除一个list的值,并获取"""
        ret = self.redis_client.lpop(key)
        return ret

    def r_llen(self, key: str) -> int:
        """list:获取list长度"""
        length = self.redis_client.llen(key)
        return length

    def r_lrange(self, key: str, start: int, end: int) -> []:
        """list:获取list指定位置的值,不删除"""
        ret = self.redis_client.lrange(key, start, end)
        return ret

    def r_hset(self, name, key, value):
        """map:插入map"""
        self.redis_client.hset(name, key, value)

    def r_hget(self, name, key):
        """map:获取name中的一个key"""
        ret = self.redis_client.hget(name, key)
        return ret

    def r_hgetall(self, name):
        """map:获取name所有的key"""
        ret = self.redis_client.hgetall(name)
        return ret

    def r_hdel(self, name, *keys):
        """map:删除name中的一个key"""
        self.redis_client.hdel(name, *keys)

    def r_sadd(self, key: str, *value):
        """set:插入集合"""
        self.redis_client.sadd(key, *value)

    def r_sismember(self, key: str, value) -> int:
        """set:判断 value元素是否集合key的成员"""
        count = self.redis_client.sismember(key, value)
        return count

    def r_del(self, *names):
        """redis:删除keys"""
        count = self.redis_client.delete(*names)
        return count


if __name__ == '__main__':
    mongo_redis = MongoRedisManager()
    mongo_redis.r_sadd("slave_id_set", "slave_2")
    # print(mongo_redis.r_del('redisKey', 'test'))
    lt = mongo_redis.redis_client.keys('*')
    print(lt)
    print(mongo_redis.redis_client.smembers("slave_id_set"))
    # print(mongo_redis.r_lpop("strList"))
    # print(mongo_redis.r_llen("strList"))
    # print(mongo_redis.r_lrange("strList", 0, -1))
    # mongo_redis.r_hset("testMap", "tt", "test")
    print(mongo_redis.r_hgetall("testMap"))
    # mongo_redis.r_lpush("testList", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    ll = mongo_redis.r_lrange("testList", 0, -1)
    print(ll)
    # tt = mongo_redis.r_lpop("testList")
    # print(tt)
    # print(type(tt))
