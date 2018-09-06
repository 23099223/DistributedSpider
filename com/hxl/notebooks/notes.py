# 信息集合
packages = {
    "spider_id": "爬虫编号,用于区分不同的爬虫",
    "sig_type": "包描述,logout(master注销slave),wait(收到wait信号时,slave暂挂后台,轮循向master请求,"
                "当没有url队列且程序并没有结束时发送wait),login(slave请求注册),spide(表示爬取url),error(待考虑)",
    "url_info": {"depth": "爬取层次,根据不同的层次使用不同的xpath", "url": "网址"},
    "content": "爬虫返回结果,最终结果或url集合,url集合:根据此次的depth寻找下一个depth,然后与url一起插入spider_id_list",
    "slave_id": "奴隶id",
    "msg_code": "返回编码,1-失败,0-成功,若失败将url放入失败池中,成功则保存返回信息"
}

# redis数据结构
spider_id_list = [{"depth": "爬取层次,根据不同的层次使用不同的xpath", "url": "网址"}, {"depth": "", "url": ""}]  # url集合
slave_id_set = ["slave_id_1", "slave_id_2", "..."]  # slave集合
logout_set = ["slave_id_1", "slave_id_2", "..."]  # slave集合
depth_list = ["xpath1", "xpath2", "xpath3", "..."]  # 严格保持顺序
running_list = ["url", "url", "..."] # 正在爬取的url,爬取成功后删除,用于检查程序是否结束
