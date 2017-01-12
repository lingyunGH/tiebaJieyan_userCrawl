#-*-coding=utf-8-*-
import scrapy
from tiebaJieyan2.items import userInfo
from json import loads
from mysql_model import Mysql
from scrapy.http import FormRequest
from tiebaJieyan2.pipelines import postsPipeline,userImgPipeline
from tiebaJieyan2.common.logger import Logger


loger = Logger('userCrawl','userSpider.log')
mysql = Mysql()
from re import findall,compile
#匹配除了数字以为的其他任意字符
regex = compile(r'\D')

class userSpider(scrapy.Spider):
    name = "userJieyan"
    #指定该爬虫执行的pipline
    pipeline = set([userImgPipeline, postsPipeline,])

    def __init__(self, offset=0, order='asc',rows=1000,*args, **kwargs):
        super(userSpider, self).__init__(*args, **kwargs)
        self.offset = int(offset)
        self.rows = int(rows)
        self.order = order

    #带参数的http请求
    def start_requests(self):
        sql = "select user_name from user order by id %s limit %d,%d;"%(self.order,self.offset,self.rows)
        # 返回查询结果
        data = mysql.find_data(sql)
        url = "http://tieba.baidu.com/home/get/panel"
        #存储多个requests请求
        requests = []
        for user_name in data:
            #参数列表
            formdata = {"un": user_name}
            request = FormRequest(url, callback=self.parse, formdata=formdata)
            requests.append(request)
        return requests


    def parse(self, response):

        user_info = userInfo()
        # 保存用户信息json
        user_info_json = loads(response.body)
        #解析为json文件，获取用户信息
        all_user_info = user_info_json['data']
        # loger.info(all_user_info)

        user_name = all_user_info['name']
        user_info['user_name'] = user_name
        # print u'姓名是:%s'%user_name
        #获取id
        user_id = all_user_info['id']
        user_info['user_id'] = user_id
        #性别
        sex = all_user_info['sex']
        user_info['sex'] = sex
        # print u'性别%s'%sex
        #发帖数目
        post_num = all_user_info['post_num']
        # print type(post_num)
        #匹配以万为单位数目
        if regex.findall(u'%s'%post_num):
            user_info['post_num'] = int(compile('\d+').findall(post_num)[0])*10000
        else:
            user_info['post_num'] = post_num
        # print u'发帖数目%s'%user_info['post_num']

        #吧龄
        tb_age = all_user_info['tb_age']
        user_info['tb_age'] = tb_age
        # print u'吧龄%s'%tb_age

        #用户头像
        portrait = all_user_info['portrait_h']
        #用户头像在网络上的URL
        user_info['portrait_url'] = 'http://tb.himg.baidu.com/sys/portrait/item/' + portrait+'.jpg'
        #图片在本地存储地址,存储绝对路径
        # user_info['portrait_path'] = '%s.jpg'%portrait


        #关注他的人数目
        followed_count = all_user_info['followed_count']
        user_info['followed_count'] = followed_count

        #关注的贴吧
        forum_title = ''
        if all_user_info['honor']['grade']:
            for forum in all_user_info['honor']['grade']:
                forum_list =  all_user_info['honor']['grade']['%s'%forum]['forum_list'][0]
                forum_title += forum_list + ','
        else:
            forum_title = ''
        # print u'关注的贴吧:%s'%forum_title
        user_info['forum_title'] = forum_title

        #管辖的贴吧(吧主)
        manager_frum = ''
        try:
            if all_user_info['honor']['manager']:
                manager_frum_one = all_user_info['honor']['manager']['manager']['forum_list'][0]
                manager_frum += manager_frum_one +','
        except KeyError:
            manager_frum = ''
        # print u'管辖的贴吧：%s'%manager_frum
        user_info['manager_frum'] = manager_frum
        # 用户详细信息页
        # user_home = "http://tieba.baidu.com/home/main/?un=" + user_name
        # user_info['user_home'] = user_home
        # print u'用户主页是:%s'%user_home


        yield user_info

























