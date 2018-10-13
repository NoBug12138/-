# -*- coding: utf-8 -*-
import hashlib
import json
import execjs
import scrapy
import time

class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ['toutiao.com']
    start_urls = ['https://www.toutiao.com/']

    def parse(self, response):
        content = {}
        j = json.loads(response.text)

        for k in range(0, 10):
            try:
                now = time.time()
                content['标题'] = j['data'][k]['title']
                content['作者'] = j['data'][k]['source']
                content['文章链接'] = 'https://www.toutiao.com/' + j['data'][k]['source_url']
                try:
                    content['评论'] = j['data'][k]['comments_count']  # 评论
                except:
                    content['评论'] = ''

                content['频道名'] = j['data'][k]['tag']  # 频道名
                try:
                    content['标签'] = j['data'][k]['label']  # 标签
                except:
                    content['标签'] = ''
                try:
                    content['文章摘要'] = j['data'][k]['abstract']  # 文章摘要
                except:
                    content['文章摘要'] = ''

                behot = int(j['data'][k]['behot_time'])
                content['发布时间'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(behot))
                content['抓取时间'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
                print(content)
            except:
                continue

        self.f = open(r"./JinRiTouTiao/sig.js", 'r', encoding='UTF-8')
        line = self.f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = self.f.readline()
        ctx = execjs.compile(htmlstr)
        Honey = json.loads(ctx.call('get_as_cp_signature'))
        max_behot_time = int(time.time())
        e = str('%X' % max_behot_time)  # 格式化时间
        m1 = hashlib.md5()  # MD5加密
        m1.update(str(max_behot_time).encode(encoding='utf-8'))  # 转化格式
        i = str(m1.hexdigest()).upper()  # 转化大写
        n = i[0:5]  # 获取前5位
        a = i[-5:]  # 获取后5位
        s = ''
        r = ''
        for x in range(0, 5):
            s += n[x] + e[x]
            r += e[x + 3] + a[x]
        eas = 'A1' + s + e[-3:]
        ecp = e[0:3] + r + 'E1'
        signature = Honey['_signature']
        return scrapy.Request(
            url='https://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1&max_behot_time=0&max_behot_time_tmp=0&tadrequire=true&as={}&cp={}&_signature={}'.format(eas, ecp, signature),
            callback=self.parse
        )