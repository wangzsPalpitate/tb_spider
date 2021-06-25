import re
import time
import requests
from loguru import logger
import pandas as pd
from time import strftime,gmtime
from clean_data import get_goods_info, collections, addresss, count, find_category


class TMSpider(object):
    def __init__(self, cookie):
        self._cookie = cookie

    def get_ip(self):
        proxy = ''
        return proxy

    def total_page(self,data):
        logger.info(data)
        # page_data = json.loads(data)
        total_num = data['total_page']
        return total_num

    def params(self,page, shop_id):
        params = {
            'sort': 'd',
            'p': page,
            'page_size': '12',
            'from': "h5",
            'shop_id': shop_id,
            'ajson': '1',
            '_tm_source': 'tmallsearch',
        }
        return params

    def headers(self):
        logger.info(self.cookie)
        headers = {
            'accept': '*/*',
            'cookie':self.cookie,
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        }
        return headers

    def get_url(self):
        shop_url = ''
        return shop_url

    def pc_headers(self):
        logger.info(self.cookie)
        pc_headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': self.cookie,
            'referer': 'https://market.m.taobao.com/',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        return pc_headers

    def write_sql(self,data):
        result = pd.DataFrame(columns=(
        'shop_id', 'shop_name', 'total_number', 'shop_url', 'goods_id', 'goods_name', 'img_url', 'goods_url',
        'sales_30', 'now_price','collection','shipping_address','brand','category_id','spu_id','comment','original_price','category_name'))
        shop_id = data.get('shop_id')
        shop_name = data.get('shop_title')
        total_number = data.get('total_results')
        shop_url = data.get('shop_Url')
        for info in data.get('items'):
            goods_id = info.get('item_id')
            goods_name = info.get('title')
            img_url = info.get('img')
            goods_url = info.get('url')
            sales_30 = info.get('sold')
            price = info.get('price')
            update_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            html_text = get_goods_info(goods_id)
            collection = collections(goods_id)
            address_data = addresss(html_text)
            count_data = count(html_text)
            address = address_data.get('addresss')
            spu_id = address_data.get('spu_id')
            original_price = count_data.get('price')
            counts = count_data.get('count')
            brand = count_data.get('brand')
            category_id = count_data.get('category')
            category_name = find_category(category_id)
            result = result.append(
                pd.DataFrame({'shop_id': [shop_id], 'shop_name': [shop_name], 'total_number': [total_number],
                              'shop_url': [shop_url], 'goods_id': [goods_id], 'goods_name': [goods_name],
                              'img_url': [img_url], 'goods_url': [goods_url], 'sales_30': [sales_30],
                              'now_price': [price], 'create_time': [update_time], 'update_time': [update_time],
                              'collection':[collection],'shipping_address':[address],'brand':[brand],'category_id':[category_id],
                              'spu_id':[spu_id],'comment':[counts],'original_price':[original_price],'category_name':[category_name]}))

            result.to_excel('1.xlsx',index=False)

    def get_page(self,url, page,shopId,headers):
        try:
            proxy = self.get_ip()
            pa = self.params(page=page + 1, shop_id=shopId)
            res = requests.get(url=url, headers=headers, params=pa, proxies=proxy,timeout=10)
            result = res.json()
            if result.get('items'):
                logger.info(result)
                return result
            else:
                # 更换cookie继续跑
                self.set_cookie()
                logger.info(result)
                time.sleep(5)
                return self.get_page(url,page,shopId,headers)
        except Exception as e:
            logger.info(e)
            time.sleep(5)
            return self.get_page(url,page,shopId,headers)

    def run(self):
        url_list = self.get_url()
        logger.info(url_list)
        for url in url_list:
            pc_url = url.get('shop_url')
            shop_url_name = re.findall('https://(\w+).',pc_url)[0]
            m_url = 'https://{}.m.tmall.com/shop/shop_auction_search.do'.format(shop_url_name)
            logger.info('手机网址：{}'.format(m_url))
            while True:
                msg = self.get_ip()
                proxy = msg['proxy']
                try:
                    res = requests.get(pc_url, self.pc_headers(), proxies=proxy,timeout=10)
                    break
                except:
                    continue
            logger.info(res.text)
            a = re.findall('content=".*"', res.text)[-1]
            shopId = re.findall('shopId=(\d+)', a)[0]
            # userId = re.findall('userId=(\d+)', a)[0]
            # para = self.params(page=1,shop_id=shopId)
            headers = self.headers()
            res = self.get_page(page=1, headers=headers, shopId=shopId, url=m_url)
            page_size = self.total_page(res)
            for page in range(int(page_size)):
                logger.info('{}/{}'.format(page+1, page_size))
                # pa = self.params(page=page+1,shop_id=shopId)
                res = self.get_page(page=page, headers=headers, shopId=shopId, url=m_url)
                self.write_sql(res)
                time.sleep(5)






if __name__ == '__main__':
    # cookie = 'cna=owTqF9U6uHkCAXUchSGVi8e7; hng=CN%7Czh-CN%7CCNY%7C156; lid=mrs%E7%8E%8B%E6%B3%BD%E5%B8%85; enc=y4hpWB5R7N%2B3irBnxPbWfGS6RwTC4Yu4O6Mri2zlbIlt9TZ83Y6dAimGgrqup4Ys3or7Goblzd33ik1P6IMQWg%3D%3D; sgcookie=E100QG9SJo14v2iuRd4VnCowohplyeXELx6ql6ERSC23txAyGYQQTVCNFNrPyw4NP3pSA01qJn9KdI4LYUMjxLERmw%3D%3D; uc3=vt3=F8dCufHBwm8k%2F0kH4vg%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UU6lRDiKR558aA%3D%3D&nk2=DkLfVQodz2kh; t=cee492f7bed15568db2e95d6ef6ba47a; tracknick=mrs%5Cu738B%5Cu6CFD%5Cu5E05; uc4=id4=0%40U2xo9I5RvXwB9Dd3zjfoN5pL0XB%2F&nk4=0%40DCdu3SoyBi0Bz%2Bmj6Yy1bR7v%2FdI%3D; lgc=mrs%5Cu738B%5Cu6CFD%5Cu5E05; _tb_token_=e313e5056113e; cookie2=1427114900ef30e4faad8081a54f5c46; sm4=350200; OZ_SI_2061=sTime=1602749911&sIndex=6; OZ_1U_2061=vid=vf840d8e447828.0&ctime=1602749930&ltime=1602749919; xlly_s=1; _m_h5_tk=d411e55da8020c9b110797f050df7951_1602843459620; _m_h5_tk_enc=b4a91fcb36550e634540c28fd2af4695; isg=BMPDOiRXmKPvCVQpD3WMySw0UoFtOFd6JPWGCvWhDiKZtOfWfQhwyzVlKkT6FK9y; l=eBS00RBnOwWbP4SiBO5Zhurza779gIOfGsPzaNbMiInca6GFwFiWHNQV1349kdtjgtfvCety6EgFrRE9JrzU5FkDBeYIWKciK4v1y; tfstk=cywdBuOfNGKdnWmT0WCMFlgq61rdCctK5HgyeiZt6xtde9GxNR10D-2AOKfI2eHOX'
    # cookie = '_m_h5_tk=1ed230998d59b5dcf7e660c50087a2d4_1603255182088; _m_h5_tk_enc=095ae572ec74826e9eb0f400d47e7370; t=f00a36d548e328635ebacc8650631cbe; cookie2=157015ca72a5a3a6cd22659e1a3b4730; v=0; _tb_token_=7be3f1f3a3e4b; cna=LoIWGDOGj1YCAXUchlxaesG7; xlly_s=1; thw=cn; _samesite_flag_=true; ctoken=rgaBRyLEdPccbniSm7Zorhllor; ockeqeudmj=itGJBJA%3D; _w_tb_nick=tb6239094064; munb=2209496660034; WAPFDFDTGFG=%2B4cMKKP%2B8PI%2BKK8YRQ%2FEB7bERr05kL4%3D; _w_app_lg=0; sgcookie=E100sVw2QXAYPsN1R4CE3DnBMW0nxNPd5RCQrH4UnlKQWtoSWeLYcmXHUY06EIdC8cDVIcz9UKbI47Iay35thTXL%2Fw%3D%3D; unb=2209496660034; uc3=lg2=URm48syIIVrSKA%3D%3D&nk2=F5RDLj4xBp32GGhX&vt3=F8dCufHJk9KiZjKajCI%3D&id2=UUphw2GgcMqcMut9qQ%3D%3D; csg=950b4906; lgc=tb6239094064; ntm=1; cookie17=UUphw2GgcMqcMut9qQ%3D%3D; dnk=tb6239094064; skt=5a0a2d59cd8ad3d9; uc4=nk4=0%40FY4I7WDCXIpSqzAHvHhQ3HjdObEgDOU%3D&id4=0%40U2grGN4%2Ffsilr3OJQQbqorZ9Mzh%2FeQlm; tracknick=tb6239094064; _cc_=VT5L2FSpdA%3D%3D; _l_g_=Ug%3D%3D; sg=44b; _nk_=tb6239094064; cookie1=BdKH7eBXZ9utFn%2Buy2zv28zzyccH8eysrz5hTEu5x%2BY%3D; mt=ci=0_1; enc=qxTWPoBRMdCYgNNpAFylOJv2L0jP83FNpx%2Bnm0HP5nTRp1RsHvPWBN%2B8zIKx8xSsD0rEGXP%2F54V7g86LmAB4DgSDp5x84n04qC24wCN08O4%3D; hng=CN%7Czh-CN%7CCNY%7C156; uc1=cookie14=Uoe0bktB1ajdsA%3D%3D&cookie15=VT5L2FSpMGV7TQ%3D%3D&existShop=false&cookie21=W5iHLLyFfoaZ; l=eBxPg9T4OoZuBbpYBOfwourza77O-IRfguPzaNbMiOCP_JCM5LlFWZ5nnQTHCnGVnsM9R3R9l27uB4LLqPae7xv9-eGBs2JaidTh.; tfstk=c7-1Byw-HIKE73u4bdMFQncOcmjPZLhChV1wCFn936H_Ca91igZPNcJHoSZdy91..; isg=BFVVgAnpphvf_4Jn3JYU2yvcZFcPUglkXr0AjNf6EUwbLnUgn6IZNGP8_jSYNSEc'
    # url = 'https://hugoboss.m.tmall.com/shop/shop_auction_search.do'
    # pc_url = 'https://hugoboss.tmall.com/?ali_refid=a3_430583_1006:1110034607:N:Mbl8tqTt1XvHp579unXEzA%3D%3D:4c70f040086e6f3381115814e2bcef31&ali_trackid=1_4c70f040086e6f3381115814e2bcef31&spm=a230r.1.14.4'
    a = TM_spider()
    # a.get_url()
    a.set_cookie()
    a.run()
    # a.run()
    # b = a.get_cookie()
    # print(b)


