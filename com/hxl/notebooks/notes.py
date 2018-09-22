# 信息集合
packages = {
    "spider_id": "爬虫编号,用于区分不同的爬虫",
    "sig_type": "包描述,logout(master注销slave),wait(收到wait信号时,slave暂挂后台,轮循向master请求,"
                "当没有url队列且程序并没有结束时发送wait),login(slave请求注册),spide(表示爬取url),error(待考虑)",
    "url_info": {"depth": "爬取层次,根据不同的层次使用不同的xpath", "url": "网址"},
    "content": "爬虫返回结果,最终结果或url集合,url集合:根据此次的depth寻找下一个depth,然后与url一起插入spider_id_list",
    "slave_id": "奴隶id",
    "ret_msg": "返回信息,成功,失败信息,若失败将url放入失败池中,成功则保存返回信息"
}

# redis数据结构
spider_id_list = [{"depth": "爬取层次,根据不同的层次使用不同的xpath", "url": "网址"}, {"depth": "", "url": ""}]  # url集合
error_list = []  # 失败池
slave_id_set = ["slave_id_1", "slave_id_2", "..."]  # slave集合
logout_set = ["slave_id_1", "slave_id_2", "..."]  # slave集合
depth_list = ["xpath1", "xpath2", "xpath3", "..."]  # 严格保持顺序
running_map = {"url1": "depth", "url2": "depth"}  # 正在爬取的url,爬取成功后删除,用于检查程序是否结束
ret_list = []  # 最终结果


# 爬取流程
"""
1. 启动master
2. 启动slave,向master请求进行登录验证
3. 登录成功后,向master提供spider_id,master分派任务(spider_id_list),并将任务存入running_map中
4. 当spider_id_list为空时,检查running_map是否为空,为空时则程序结束,不空时向slave发送wait信号
5. 当slave获取到任务信息后,进行爬取,成功则返回结果.爬取失败次数达10次后返回error信息,
由master将次任务保存到error_list中
6. 当master收到结果信息后,根据depth获取下一个depth与返回结果包装成任务信息存入spider_id_list中
或者确定是否是最后一个depth保存到ret_list中
7. 每次收到slave请求时,master会检查slave_id是否存在logout_set中,是则发送logout信号终止slave任务


爬取编号由slave提供

"""

