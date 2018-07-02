import requests
from pyquery import PyQuery as pq
import re
import os
from settings import BASE_URL, HEADERS, MODE
from multiprocessing import Pool
from time import sleep
from hashlib import md5


'''
爬取：http://beauty.pcauto.com.cn/的2个模块（美女精选、明星车模）下所有图片
1、从http://beauty.pcauto.com.cn/获取2个模块对应的url
2、获取每个模块有多少页面，拿到对应页面url
3、分析每个页面信息，拿到每组图片的详情链接
4、从详情链接，获取具体图片
'''


def get_page(url):
    """
    获取页面信息
    :param url: url
    :return: None or text
    """
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
        else:
            print('请求：%s 出错，状态码：%s' % (url, response.status_code))
            return None
    except Exception as e:
        print('请求：%s 出错，%s' % (url, e.args))
        return None


def get_module_urls():
    """
    获取2个模块对应的url
    :return: 2个模块的url
    """
    text = get_page(BASE_URL)
    if text:
        urls = []
        doc = pq(text)
        for a in doc('.mark a').items():
            if a.attr('class') != 'cur' and a.attr('target') == '_self':
                module_url = 'http:' + a.attr('href')
                urls.append(module_url)
        return urls[:-1]


def get_one_module_all_pages_url(module_url):
    """
    获取每个模块下所有页的url
    :param module_url:
    :return:
    """
    text = get_page(module_url)
    if text:
        # urls = []
        doc = pq(text)
        # 从页面下方页码处解析出总页数
        total_page = int(doc('.pcauto_page a:nth-last-child(2)').text())
        for i in range(1, total_page+1):
            page_url = module_url.split('.html', )[0][:-1] + '{}.html'.format(i)
            # urls.append(page_url)
            parse_one_page(page_url)
        # return urls


def parse_one_page(url):
    """
    解析图组页面，拿到每组图的链接
    :param url: 页面url
    :return: 图组链接
    """
    text = get_page(url)
    if text:
        doc = pq(text)
        # detail_urls = []
        for li in doc('.ulPic.p135.clearfix li').items():
            detail_url = BASE_URL + str(li('a').attr('href')).split('..')[-1]
            print(detail_url)
            # detail_urls.append(detail_url)
            parse_detail_page(detail_url)
        # return detail_urls


def parse_detail_page(url):
    """
    解析图组详情页面，获取所有图片url
    获取一共有多少张，在url的基础上加1得到url
    :param url: 详情页面url
    :return: 图片url
    """
    text = get_page(url)
    if text:
        doc = pq(text)
        # 取出图组名称
        title = re.compile('(.*?)\(', re.S).search(doc('.mark em').text()).group(1)
        print('title:', title)
        total = int(doc('#totalImgNum').text())
        next_page_url = re.compile('nLink.*?=.*?(.*?),', re.S).search(text).group(1)
        print('next_page_url:', next_page_url)
        print('total:', total)
        first_page_no = int(re.compile('.*?(\d+).html', re.S).search(next_page_url).group(1)) - 1
        print('first_no:', first_page_no)
        for page_no in range(0, total):
            no = first_page_no + page_no
            url = BASE_URL+'/{}/{}.html'.format(MODE, no)
            print('第%s张图片url：%s' % (page_no+1, url))
            parse_img(title, url)
            sleep(1)


def parse_img(title, url):
    text = get_page(url)
    if text:
        doc = pq(text)
        img_url = 'http:' + doc('#pic_img').attr('src')
        print('图片地址：', img_url)
        download_img(title, img_url)
    else:
        print('解析图片出错：', url)


def download_img(title, url):
    print('正在下载：', url)
    response = requests.get(url)
    if response.status_code == 200:
        images_path = '{}{}images'.format(os.getcwd(), os.sep)
        if not os.path.exists(images_path):
            print('文件夹不存在，创建：', images_path)
            os.mkdir(images_path)
        img_group_path = '{}{}{}'.format(images_path, os.sep, title)
        if not os.path.exists(img_group_path):
            print('创建图组文件夹：', img_group_path)
            os.mkdir(img_group_path)
        # 将图片md5值作为图片名
        img_path = '{}{}{}.jpg'.format(img_group_path, os.sep, md5(response.content).hexdigest())
        if not os.path.exists(img_path):
            with open(img_path, 'wb') as fp:
                fp.write(response.content)
        else:
            print('该图片已存在')


if __name__ == '__main__':
    urls = get_module_urls()
    # # # 遍历模块url
    # # for module_url in urls[:-1]:
    # #     # 遍历每个模块下所有页
    # #     for page_url in get_one_module_all_pages_url(module_url):
    # #         # 分析每一页内容，得到图组url
    # #         url_groups = parse_one_page(page_url)
    # #         for detail_url in url_groups:
    # #             # 从详情url解析出每组图片包含的url
    # #             parse_detail_page(detail_url)
    #

    pool = Pool()
    pool.map(get_one_module_all_pages_url, urls)
