# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from  scrapy import Item,Field

class userInfo(Item):
    user_id = Field()
    user_name = Field()
    sex = Field()
    #发帖数目
    post_num = Field()

    # 吧龄
    tb_age = Field()

    # 关注他的人数目
    followed_count = Field()

    # 关注的贴吧
    forum_title = Field()

    # 管辖的贴吧(吧主)
    manager_frum = Field()

    #图片在网络中的位置，用于爬虫爬取
    portrait_url = Field()
    #图片在数据库中的相对路径
    portrait_path = Field()

    #用户主页
    # user_home = Field()
    # #用户所有信息的json格式
    # user_info_json = Field()
    #用户头像




