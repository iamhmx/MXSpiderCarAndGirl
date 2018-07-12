# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem


class CarAndGirlPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['image_urls']:
            yield Request(url=url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        group_name = request.meta['item']['group_name']
        image_name = request.url.split('/')[-1]
        filename = '{0}/{1}'.format(group_name, image_name)
        return filename

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for mark, x in results if mark]
        if not image_paths:
            raise DropItem('Image Download Failed')
        return item
