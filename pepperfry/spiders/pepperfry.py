import scrapy
import re
import json
import os
import requests

class pepperfrySpider(scrapy.Spider):
    name = "ppfry_spider"
    
    Max_count = 20

    Base_URL = "https://www.pepperfry.com/site_product/search?q="
    Base_Dir = "./Pepperfry-data/"
    
    items = ['two seater sofa','bench','book cases','coffee table',
            'dining set','queen bed','arm chairs','chest drawers',
            'garden seatings','bean bags','king beds']

    def start_requests(self):
        
        for item in self.items:

            query_string = '+'.join(item.split(' '))
            url = self.Base_URL + query_string

            dir_name  = "-".join(item.split(' '))

            # dir_path = self.Base_Dir + dir_name

            # if not os.path.exists(dir_path):
            #     os.makedirs(dir_path)
                

            resp = scrapy.Request(url=url, callback=self.parse,dont_filter=True)
            resp.meta['dir_name'] = dir_name

            yield resp

    def parse(self, response):
        # items_url = []
        i = 0
        while i in range(self.Max_count):
            result_items = response.css('div.clipprods')[i]
            item_url = result_items.css('div.clip-dtl-ttl div.pf-col h2 a::attr(href)').get()
            i = i+1
            
            resp = scrapy.Request(url=item_url,callback=self.parserToParse,dont_filter=True)
            resp.meta['dir_name'] = response.meta['dir_name']

            yield resp

    def parserToParse(self,response):
            product_name = response.css('h1.v-pro-ttl::text').get()
            
            dir_name = response.meta['dir_name']

            dir_path = self.Base_Dir + dir_name + '/' + '-'.join(product_name.split(' '))

            price = response.css('span.v-offer-price-amt::text').get()
            keys = response.css('span.v-prod-comp-dtls-listitem-label::text').getall()
            values = response.css('span.v-prod-comp-dtls-listitem-value::text').getall()
            
            images = response.css('a.vipGallery__thumb-img::attr(data-img)').getall()

            d={
                'product_name':product_name,
                'price':price,
            }

            for i,key in enumerate(keys):
                d[key] = values[i]

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            for i,image in enumerate(images):
                r = requests.get(image)
                with open(os.path.join(dir_path,'image_{}.jpg'.format(i+1)),'wb') as f:
                    f.write(r.content)

            
            with open(os.path.join(dir_path,'metadata.txt'),'w') as f:
                json.dump(d,f)

            yield None