import scrapy
from scrapy import Request
from violin.items import ViolinItem, MasterItem
from header import HEADER
import re
import json
import os,sys
import requests
import subprocess as sp
from twisted.internet import reactor
from .down import down_all
# reactor.suggestThreadPoolSize(1)

class ViolinSpider(scrapy.Spider):
    name = "violin"
    allow_domains = ['violinlab.com']
    start_urls = [
        'http://violinlab.com/videoLibrary/'
    ]

    def parse(self, response):
        # filename = response.url.split("/")[-2]
        # with open(filename,'wb') as f:
        #     f.write(response.body)

        for sel in response.xpath("//a[re:test(@href,'less*')]"):
            item = ViolinItem()
            item['name'] = sel.xpath("text()").extract()[
                0].replace('\t', '').replace('\n', '')
            item['link'] = "http://violinlab.com/videoLibrary/" + \
                sel.xpath('@href').extract()[0]
            HEADER['Referer'] = item['link']
            yield Request(item['link'], headers=HEADER, method='GET', callback=self.parse2)
    
    def parse2(self,response):
        print response.xpath("//div[@class='title']/text()").extract()
        link = response.xpath("//iframe/@src").extract()[0]
        HEADER['Referer'] = response.url
        request =  Request(link, headers=HEADER, method='GET', callback=self.parse3)
        request.meta['link'] = response.url
        request.meta['title'] = response.xpath("//div[@class='title']/text()").extract()
        yield request
        
        

    def parse3(self, response):
        # print response.xpath('//title/text()').extract()
        item = MasterItem()
        master = re.findall('(?:https|http)://sky[\s\S]*?master.json[\s\S]*?(?=")',response.body)[0]
        item['sky'] = master
        item['link'] = response.meta['link']
        item['title'] = response.meta['title']
        down_all(item['sky'],str(item['title'][0]).translate(None, "|\\?*<\":>+[]/'"))
        # sp.call([
        #     'python','C:\\Users\\rc452\\Desktop\\work\\vimeo-download\\vimeo-download.py','-u',item['sky'],'-o',str(item['title'])
        # ])

class SpiderTest(object):
    def test1(self):
        violin_path = 'violin\\spiders\\example\\play.html'
        print os.path.abspath('.')
        print os.path.exists(violin_path)
        with open(violin_path,'r+') as html:
            list = re.findall('(?:https|http)://[40|sky][\s\S]*?master.json[\s\S]*?(?=")',html.read())
            print json.dumps(list)
            print len(list)
    def test2(self):
        HEADER['Referer'] = "http://violinlab.com/videoLibrary/lesson.php?id=12"
        s = requests.Session()
        s.proxies = {
            'https':"http://127.0.0.1:1080"
        }
        res = s.get("https://player.vimeo.com/video/133517984",headers = HEADER)
        with open("violin\\spiders\\example\\b.html",'w') as file:
            file.write(res.text)
    def test3(self):
        data = json.loads(open('item2.json').read())
        count = 0
        for item in data:
            if len(item['serial']) > 10:
                count +=1
        print count
        
if __name__ == "__main__":
    SpiderTest().test3()