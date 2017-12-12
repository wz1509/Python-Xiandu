#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import urllib2
import cookielib
from bs4 import BeautifulSoup


class Xiandu:
    def __init__(self):
        self.siteGankURL = 'http://gank.io'
        self.siteURL = 'http://gank.io/xiandu'
        self.conn = mysql.connector.connect(user='wz', password='123456', database='test', use_unicode=True)

    def getCookie(self):
        filename = 'cook.txt'
        cookie = cookielib.MozillaCookieJar()
        cookie.load(filename, ignore_discard=True, ignore_expires=True)
        return cookie

    def getBeautifulSoup(self, url):
        req = urllib2.Request(url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.getCookie()))
        response = opener.open(req)
        html = response.read()
        soup = BeautifulSoup(html)
        # print soup.prettify()
        return soup

    # 创建标签表
    def createCat(self):
        cursor = self.conn.cursor()
        sql = 'Create Table If Not Exists table_cat(id integer unsigned Primary key Auto_Increment,href_url ' \
              'varchar(50) not null, name varchar(50) not null)'
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    # 创建内容表
    def createContent(self):
        cursor = self.conn.cursor()
        sql = "Create Table If Not Exists table_content(span_index " \
              "varchar(10) not null, href_url varchar(200) not null, descs varchar(100) not null,public_at varchar(" \
              "50) not null, site_href varchar(200) not null, site_title varchar(100) not null,site_img varchar(200) " \
              "not null)ENGINE=InnoDB DEFAULT CHARSET=utf8"
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    # 根据sql查询
    def selectTable(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    # 获取闲读标签类
    def getXianduCatList(self):
        cursor = self.conn.cursor()
        sql = 'delete from table_cat'
        cursor.execute(sql)
        self.conn.commit()

        soup = self.getBeautifulSoup(self.siteURL)
        xiandu_cat = soup.find_all(id='xiandu_cat')
        for tag_a in xiandu_cat:
            cats = tag_a.find_all('li')
            for cat in cats:
                for i in range(len(cat.find_all('a'))):
                    cat = cat.find_all('a')[i]
                    href = cat.get('href')
                    string = cat.string
                    print(href + '---' + string)
                    sql = 'insert into table_cat(id,href_url,name) values(' + str(
                        i) + ',"' + href + '","' + string + '")'
                    cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        print '插入数据成功'

    # 获取闲读内容
    def getXianduContent(self, cat, page):
        cursor = self.conn.cursor()
        sql = 'delete from table_content'
        cursor.execute(sql)
        self.conn.commit()

        soup = self.getBeautifulSoup(self.siteGankURL + cat + '/page/' + str(page))
        # print soup.prettify()
        items = soup.find_all('div', class_='xiandu_item')
        for i in range(len(items)):
            item = items[i]
            spanIndex = item.span.string
            href = item.a.get('href')
            text = item.a.string
            smallTxt = item.small.string.strip()
            site_href = item.find('a', class_='site-name').get('href')
            site_title = item.find('a', class_='site-name').get('title')
            site_img = item.find('a', class_='site-name').find('img', class_='site-img').get('src')
            sql = 'insert into table_content(span_index,href_url,descs,public_at,site_href,site_title,site_img)' \
                  ' values("' + spanIndex + '","' + href + '","' + text + '","' + smallTxt + '","' + site_href + '","' \
                  + site_title + '","' + site_img + '")'
            cursor.execute(sql)
            self.conn.commit()

        cursor.close()
        print '插入数据成功'


xd = Xiandu()
xd.createCat()
xd.getXianduCatList()

xd.createContent()
xd.getXianduContent('/xiandu/wow', 2)

sql = 'select * from table_content'
for item in xd.selectTable(sql):
    print item
