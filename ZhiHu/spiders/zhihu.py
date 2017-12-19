# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import ZhihuItem
class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    deep=3
    first_name='excited-vczh'
    info_url = 'https://www.zhihu.com/api/v4/members/{user}?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    focus_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={offset}&limit=20'
    def start_requests(self):
        yield scrapy.Request(url=self.info_url.format(user=self.first_name),callback=self.parse_data)
        yield scrapy.Request(url=self.focus_url.format(user=self.first_name,offset=0),meta={'deep':1},callback=self.parse_user)

    def parse_data(self, response):
        item=ZhihuItem()
        dic=json.loads(response.text)
        item['name']=dic['name']
        if dic['gender']==1:
            item['gender']='男'
        else:
            item['gender'] = '女'
        item['follower_count']=dic['follower_count']
        if 'headline' in dic.keys() and dic['headline']!='':
            item['headline']=dic['headline']
        else:
            item['headline']='该信息不存在'
        if dic.get('employments')!=[]:
            if 'company' in dic['employments'][0].keys() and dic['employments'][0]['company']:
                item['company'] = dic['employments'][0]['company']['name']
            else:
                item['company'] = '公司未注明'
            if 'job' in dic['employments'][0].keys() and dic['employments'][0]['job']:
                item['job'] = dic['employments'][0]['job']['name']
            else:
                item['job'] = '工作未注明'
        else:
            item['company'] = '公司未注明'
            item['job'] = '工作未注明'
        yield item
        next_user_url = self.focus_url.format(user=dic.get('url_token'),offset=0)
        yield scrapy.Request(next_user_url, meta={'deep': 1}, callback=self.parse_user)

    def parse_user(self,response):
        dic=json.loads(response.text)
        print('判断一下',response.meta['deep'])
        #解析返回的user页面 得到数据页面的url 返回给数据解析函数
        if 'data' in dic.keys():
            for follow in dic['data']:
                url_token=follow['url_token']
                next_data_url=self.info_url.format(user=url_token)
                yield scrapy.Request(next_data_url,callback=self.parse_data)
        #判断翻页和判断爬取深度
        if 'paging' in dic.keys() and dic.get('paging').get('is_end')==False and response.meta['deep']<self.deep:
            next_page=dic.get('paging').get('next')
            yield scrapy.Request(next_page, meta={'deep': response.meta['deep'] + 1}, callback=self.parse_user)

