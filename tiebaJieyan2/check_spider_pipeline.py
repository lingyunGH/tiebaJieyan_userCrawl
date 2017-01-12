#-*-coding=utf-8-*-
import functools
#定义装饰器，用于多个爬虫的时候使用不同的pipline
def check_spider_pipeline(process_item_method): #判断爬虫执行那些脚本的装饰器
    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):
        # message template for debugging
        msg = '%%s %s pipeline step' % (self.__class__.__name__,)
# if class is in the spider's pipeline, then use the
        # process_item method normally.
		#判断当前的pipline是否在当前爬虫的pipline中
        if self.__class__ in spider.pipeline:
            spider.logger.debug(msg % 'executing')
            return process_item_method(self, item, spider)
# otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            spider.logger.debug(msg % 'skipping')
            return item
    return wrapper