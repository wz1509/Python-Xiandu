#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import cookielib
from bs4 import BeautifulSoup
import sys
import re

from pip._vendor import requests


class meizhi:
    def __init__(self):
        self.siteURL = 'http://www.mmjpg.com/'
        self.save_pic_path = '/Users/threebears/Downloads/mmJPG/'

    def getCookie(self):
        filename = 'cook.txt'
        cookie = cookielib.MozillaCookieJar()
        cookie.load(filename, ignore_discard=True, ignore_expires=True)
        return cookie

    def getBeautifulSoup(self, url):
        req = urllib2.Request(url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.getCookie()))
        response = opener.open(req, timeout=10)
        html = response.read()
        soup = BeautifulSoup(html)
        # print soup.prettify()
        return soup

    def crawlData(self, page):
        url = self.siteURL
        if page != 1:
            url += 'home/' + str(page)

        # 创建文件夹
        self.create_dir_path()

        # 开始爬取数据
        soup = self.getBeautifulSoup(url)
        items = soup.find_all('div', class_='pic')[0].find('ul').find_all('li')
        for item in items:
            title = item.find('a').find('img').get('alt')
            imageUrl = item.find('a').find('img').get('src')
            self.download_pic(imageUrl, title + '.jpg')

    # 创建文件夹
    def create_dir_path(self):
        exists = os.path.exists(self.save_pic_path)
        if not exists:
            print '创建文件夹'
            os.makedirs(self.save_pic_path)
        else:
            print '文件夹已存在'

    # 保存图片到本地
    def download_pic(self, pic_url, pic_name):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Referer': "http://www.mmjpg.com"
        }
        try:
            # 设置绝对路径，文件夹路径 + 图片路径
            path = self.save_pic_path + pic_name
            if os.path.isfile(path):
                print('该图片已存在  ' + pic_name)
                return
            print('文件路径：' + path + ' 图片地址：' + pic_url)
            try:
                img = requests.get(pic_url, headers=headers, timeout=10)
                with open(path, 'ab') as f:
                    f.write(img.content)
                    print(path)
            except Exception as e:
                print(e)

            print "保存图片完成"
        except Exception, e:
            print e
            print "保存图片失败: " + pic_url

    # 获取总页码
    def get_page(self):
        soup = self.getBeautifulSoup(self.siteURL)
        string_page = soup.find_all('div', class_='page')[0].find('em', class_='info').string.strip()
        int_page = int(re.findall('\d+', string_page)[0])
        return int_page


# 指明解码方式
reload(sys)
sys.setdefaultencoding('utf-8')

meizhi = meizhi()
max_page = meizhi.get_page() + 1
print(max_page)
for page in range(1, max_page):
    meizhi.crawlData(page)
print('------------->>>>>>>>>>>>>>爬取完成')
