from scrapy import Spider
from scrapy.http import Request
from ..settings import BASE_URL, MODE
import re
from ..items import CarAndGirlItem


class CarAndGirlSpider(Spider):
    name = 'carandgirl'
    start_urls = [BASE_URL]
    img_urls = []

    def parse(self, response):
        for module_url in response.css('.mark a[target="_self"]::attr("href")').extract()[1:-1]:
            print('module_url:', response.urljoin(module_url))
            yield Request(response.urljoin(module_url), callback=self.parse_module)

    def parse_module(self, response):
        print('res:', response)
        # 解析出每一页的详情页面地址
        for detail_url in response.css('.ulPic.p135.clearfix li a::attr("href")').extract():
            print('detail_url:', response.urljoin(detail_url))
            yield Request(response.urljoin(detail_url), callback=self.parse_detail_page)
        # 解析出每一页的地址
        for page_url in response.css('.pcauto_page a::attr("href")').extract()[:-1]:
            print('page_url:', response.urljoin(page_url))
            yield Request(response.urljoin(page_url), callback=self.parse_module)

    def parse_detail_page(self, response):
        # 取出图组名称
        item = CarAndGirlItem()
        title = response.css('.mark em a::text').extract_first()[:-1]
        item['group_name'] = title
        # print('title: ', title)
        # 取出图片总数
        total = int(response.css('#totalImgNum::text').extract_first())
        # print('total: ', total)
        next_page_url = re.compile('nLink.*?=.*?(.*?),', re.S).search(response.text).group(1)
        # print('next_page_url: ', next_page_url)
        first_page_no = int(re.compile('.*?(\d+).html', re.S).search(next_page_url).group(1)) - 1
        for page_no in range(0, total):
            no = first_page_no + page_no
            url = BASE_URL+'/{}/{}.html'.format(MODE, no)
            print('第%s张图片url：%s' % (page_no+1, url))
            yield Request(url, callback=self.parse_image)
        item['image_urls'] = self.img_urls
        yield item

    def parse_image(self, response):
        url = 'http:' + response.css('#pic_img::attr("src")').extract_first()
        self.img_urls.append(url)
