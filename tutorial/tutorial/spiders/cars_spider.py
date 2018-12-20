#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import sys
import requests
import os
reload(sys)
sys.setdefaultencoding('utf-8')


class CarsSpider(scrapy.Spider):
    name = "cars"

    def __init__(self):
        self.term = 331
        self.total_count=0
        self.pageSize = 16
        self.bidPageSize = 10
        self.pageNum = 0
        page = '4'
        self.filename = '../cars-%s.html' % page


    def start_requests(self):
        
        if os.path.isfile(self.filename):
            os.remove(self.filename)

        url = 'https://otc.cbex.com/page/jpxkc/zc_prjs/index?id=%s' % self.term

        yield scrapy.Request(url, callback=self.get_total_num)

    def get_total_num(self, response):
        self.total_count = Selector(text=response.body).css('div .zc_banner_info_bm p:first-child span::text').extract()
        self.log(self.total_count[0])
        nums = int((int)(self.total_count[0])/self.pageSize) + 1
        self.log(nums)
        for no in range(1,nums+1):
            self.log(no)
            formdata={'id': '331', 'pageNo': str(no), 'pageSize': str(self.pageSize), '_totalCount': str(int(self.total_count[0]))}
            self.log(formdata)
            url = 'https://otc.cbex.com/page/jpxkc/zc_prjs/prj_li'
            yield scrapy.FormRequest(url, formdata=formdata, callback=self.get_cars_list)
    
    def get_cars_list(self,response):

        #cars_list = Selector(text=response.body).css('.num::text').extract()
        carslist_selector = Selector(text=response.body).css('li')
        for i in range(len(carslist_selector)):
            #编号,价格,链接,图片,车牌号,车牌号全名,成交价,最高限价
            l = (no,price,link,image,carno,carfullno,dealprice,highprice) = (\
                carslist_selector[i].css('li::attr(data-xmid)')[0].extract(),  \
                carslist_selector[i].css('li::attr(data-price)')[0].extract(), \
                "https://otc.cbex.com" + carslist_selector[i].css('li a::attr(href)')[0].extract(), \
                "https://otc.cbex.com" + carslist_selector[i].css('li a img::attr(data-original)')[0].extract(), \
                carslist_selector[i].css('li a div').css('.num::text')[0].extract(),    \
                carslist_selector[i].css('li div').css('.cont').css('a::text')[0].extract(),    \
                carslist_selector[i].css('li div').css('.cont').css('div .info span[class^="fs18"]::text')[0].extract(),    \
                carslist_selector[i].css('li div').css('.cont').css('div .info span[class^="color_theme"]::text')[0].extract())

            headers = {
                'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
            }
            r = requests.get(link, headers=headers)

            maxNumber = Selector(text=r.content).xpath('//span[@id="bj_countId"]/text()')[0].extract()
            #print "最高限价报价人数:" + maxNumbers

            with open(self.filename, 'ab') as f:
                # f.write(str(tup).encode('utf-8').decode('unicode_escape') + '\n')
                f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(no,price,link,image,carno,carfullno,dealprice,highprice,maxNumber))
            
            nums = int((int)(maxNumber)/self.bidPageSize) + 1
            for no1 in range(1,nums+1):
                formdata={'id': str(no), 'pageNo': str(no1), 'pageSize': str(self.bidPageSize)}
                url = 'https://otc.cbex.com/page/jpxkc/prj/jjjgListPaging'
                m1 = (l,maxNumber)
                self.log(m1)
                yield scrapy.FormRequest(url, formdata=formdata, callback=lambda l:self.parse_car_bidding_persion(l))
            
            

    # def get_car_bidding_person(self):
    #     self.log("get_car_bidding_personget_car_bidding_personget_car_bidding_person")
    #     url = 'https://otc.cbex.com/page/jpxkc/prj/jjjgListPaging'
    #     with open(self.filename, 'r') as f:
    #         pageNo = 1
    #         for line in f:
    #             lineArr = line.split(',')
    #             maxNumber = lineArr[8]
    #             nums = (int)(maxNumber/self.bidPageSize) + 1
    #             id = lineArr[0]
    #             formdata={'id': id, 'pageNo': str(pageNo), 'pageSize': str(self.bidPageSize)}
    #             #callback 传参数 用lambda
    #             yield scrapy.FormRequest(url, formdata=formdata, callback=lambda l: self.parse_car_bidding_persion(l))

    
    def parse_car_bidding_persion(self, m):
        self.log("进入")
        page = '6'
        filename = '../cars-%s.html' % page
        # if os.path.isfile(filename):
        #     os.remove(filename)
        with open(filename, 'ab') as f:
                f.write("%s,%s\n" %(str(m),"1"))


    def parse(self, response):
        page = 7
        filename = 'cars-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)