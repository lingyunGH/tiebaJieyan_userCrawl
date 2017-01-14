# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
#丢弃无用的pipline
from scrapy.exceptions import DropItem
from tiebaJieyan2.items import userInfo
import MySQLdb
import MySQLdb.cursors
from scrapy.utils.project import get_project_settings
from scrapy import log
from tiebaJieyan2.common.logger import Logger
from tiebaJieyan2.check_spider_pipeline import check_spider_pipeline
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline

loger = Logger('userPipline','userPipline.log')
#载入设置
SETTINGS = get_project_settings()


class userImgPipeline(ImagesPipeline):  # 继承ImagesPipeline这个类，实现这个功能

    def get_media_requests(self, item, info):  # 重写ImagesPipeline   get_media_requests方法
        '''
        :param item:
        :param info:
        :return:
        在工作流程中可以看到，
        管道会得到文件的URL并从项目中下载。
        为了这么做，你需要重写 get_media_requests() 方法，
        并对各个图片URL返回一个Request:
        '''
        # for image_url in item['portrait_url']:
        #     yield Request(item['portrait_url'])
        # print  item['portrait_url']
        #下载图片
        # loger.info(item['portrait_url'])
        if isinstance(item,userInfo):
            yield Request(item['portrait_url'])
            # loger.info(item['portrait_url'])

    #避免下载重复图片
    def item_completed(self, results, item, info):
        '''

        :param results:
        :param item:
        :param info:
        :return:
        当一个单独项目中的所有图片请求完成时（要么完成下载，要么因为某种原因下载失败），
         item_completed() 方法将被调用。
        '''
        # loger.info('%s'%results)
        image_paths = [x['path'] for ok, x in results if ok]
        # loger.info(image_paths)
        if not image_paths:
            raise DropItem("Item contains no images,results is %s,item is %s"%(results,item))

        #存储路径
        item['portrait_path'] = image_paths[0].split('/')[1]
        return item

class postsPipeline(object):
    loger.info('enter postsPipline' )
    def __init__(self):
        #数据库链接操作
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                                            host=SETTINGS['DB_HOST'],
                                            user=SETTINGS['DB_USER'],
                                            passwd=SETTINGS['DB_PASSWD'],
                                            port=SETTINGS['DB_PORT'],
                                            db=SETTINGS['DB_DB'],
                                            charset='utf8',
                                            use_unicode=True,
                                            cursorclass=MySQLdb.cursors.DictCursor)

    def spider_closed(self, spider):
        """ Cleanup function, called after crawing has finished to close open
            objects.
            Close ConnectionPool. """
        self.dbpool.close()

    #使用定义的pipline
    @check_spider_pipeline
    def process_item(self, item, spider):

        # run db query in thread pool
        #判断是哪个item，用于只有指定的item才可以执行该pipline
        if isinstance(item,userInfo):
            query = self.dbpool.runInteraction(self._conditional_insert, item)
            query.addErrback(self.handle_error)
            return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist.
        # all this block run on it's own thread
        sql1 = 'set names utf8mb4'
        tx.execute(sql1)
		try:
			args = (item['user_id'],
					item['user_name'],
					item['sex'],
					item['post_num'],
					item['tb_age'],
					item['followed_count'],
					item['forum_title'],
					item['manager_frum'],
					item['portrait_path']
					)
			sql = "insert into user_detail(user_id,user_name,sex,post_num,tb_age,followed_count,forum_title,manager_frum,portrait) VALUES(%s,'%s','%s',%d,'%s',%d,'%s','%s','%s')" % args
			tx.execute(sql)
			log.msg("Item stored in db: %s" % item, level=log.INFO)

		except：
		# 避免重复存储
			# log.msg("threads_id already stored in db: %s" % item, level=log.WARNING)
			# 更新帖子信息
			args = (item['user_name'],
					item['post_num'],
					item['tb_age'],
					item['followed_count'],
					item['forum_title'],
					item['manager_frum'],
					item['portrait_path'],
					item['user_id']
					)
			# sql后面
			sql = "UPDATE user_detail SET user_name='%s', post_num=%d,tb_age='%s',followed_count=%d,forum_title='%s',manager_frum='%s',portrait='%s'  WHERE user_id='%s'" % args
			# print sql
			# loger.info(sql)
			# 执行更新操作
			tx.execute(sql)
			log.msg("update item : %s" % item, level=log.WARNING)
			
        except KeyError:
            DropItem(u'missing thread_id:%s' % item)


    def handle_error(self, e):
        log.err(e)



