#coding=utf-8
import json
import re
import time
import requests
from loguru import logger


def get_ip():

    proxy = ''
    return proxy


def get_goods_info(goods_id):
    while True:
        proxy = get_ip()
        header = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://market.m.taobao.com/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        }
        try:
            url = 'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.180.519346c6eHkwrY&id={}'.format(goods_id)
            res = requests.get(url=url,headers=header, proxies=proxy, timeout=10)
            data_detail = re.findall('_DATA_Mdskip = \W+(.*)} </script>', res.text)[0]
            data_json = json.loads('{"' + data_detail + '}')
            logger.info(data_json)
            delivery_json = data_json.get('delivery')
            address = delivery_json.get('from')
            item_data = data_json.get('item')
            spu_id = item_data.get('spuId')
            return res.text
        except Exception as e:
            logger.info(e)
            continue


# 获取收藏人数
def collections(item_id):

    millis = int(round(time.time() * 1000))
    url = 'https://count.taobao.com/counter3?_ksTS={}_258&callback=jsonp259&keys=SM_368_dsr-2253628731,ICCP_1_{}'.format(millis, item_id)
    header = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://market.m.taobao.com/',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }
    while True:
        try:
            msg = get_ip()
            proxy = msg['proxy']
            res = requests.get(url=url, headers=header, proxies=proxy,timeout=10)
            logger.info(res.text)
            collectionss = re.findall('"ICCP_1_\d+":(\d+)',res.text)[0]
            return collectionss
        except Exception as e:
            logger.info(e)
            continue


def find_category(id):
    """
    获取商品三级类目，需要找人添加白名单，
    :param id:
    :return:
    """
    while True:
        url = 'http://app.miiow.com.cn:8181/ajaxApi.ashx/@/dontlogin/sycm/getCateInfo?cateId={}&userId=599782682'.format(id)
        headers = {
            'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'Host':'app.miiow.com.cn:8181',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
        }
        try:
            resp = requests.get(url=url,headers=headers,timeout=10)
            # resp.status_code
            try:
                result_list = resp.json()
                logger.info(resp.json())
            except:
                result_list = resp.text
                logger.info(resp.text)

            if result_list:
                logger.info(type(result_list))

                try:
                    category_name = re.findall('"path":"(.*)","name"',str(result_list))[0]
                except:
                    category_name = re.findall("'path':(.*)', 'name'",str(result_list))[0]
                logger.info(category_name)
                return category_name
            else:
                logger.info('无类目{}'.format(id))
                return '无类目'
        except Exception as e:
            logger.info(e)
            continue






# 发货地址
# def shipping_address(html):
#     address= re.findall(' <input type="hidden" name="region" value="([\u4e00-\u9fa5]+)', html)[0]
#     return address

# # 扣出htm里面的数据
# def html_data(html):
#     html_json = re.findall('{"valItemInfo":.*',html)[0]
#     data_json = json.loads(html_json)
#     #品牌json
#     brand_json = data_json.get('itemDO')
#     brand = brand_json.get('brand')
#     #三级类目id
#     category = brand_json.get('categoryId')
#     #spu_id
#     spu_id = brand_json.get('spuId')
#     return {'brand':brand,'category':category,'spu_id':spu_id}

# 评论和原价
def count(html):
    data_detail = re.findall('_DATA_Detail = (.*)</script>',html)[0]
    json_data = json.loads(data_detail[:-1])
    logger.info(json_data)
    count_number = json_data.get('rate')
    if count_number:
        totalCount = count_number.get('totalCount')
    else:
        totalCount = None
    # try:
    price_json = json_data.get('mock')
    price_data = price_json.get('price')
    price_dict = price_data.get('price')
    priceText = price_dict.get('priceText')
    item_data = json_data.get('item')
    category = item_data.get('categoryId')
    props_data = json_data.get('props')
    groupProps = props_data.get('groupProps')
    deatli_list = groupProps[0]
    brand_list = deatli_list['基本信息']
    brand_dict = {}
    for brand in brand_list:
        brand_dict.update(brand)
    brand_name = brand_dict.get('品牌')
    return {'price': priceText, 'count': totalCount, 'brand': brand_name, 'category': category, }
    # except:
    #     return {'price': '无价格', 'count': '无评论量', 'brand': '无品牌', 'category': , }

    # # return totalCount
    # logger.info(json_data)
    # logger.info(priceText)

# 发货地址
def addresss(html):
    try:
        data_detail = re.findall('_DATA_Mdskip = \W+(.*)} </script>', html)[0]
    except:
        logger.info('html出现问题，没定位到数据')
        return {'addresss': '无发货地', 'spu_id': '无spu'}
        # logger.info(html)
    data_json = json.loads('{"' + data_detail + '}')
    logger.info(data_json)
    delivery_json = data_json.get('delivery')
    address = delivery_json.get('from')
    item_data = data_json.get('item')
    spu_id = item_data.get('spuId')
    return {'addresss': address, 'spu_id': spu_id}






if __name__ == '__main__':
    a = get_goods_info(621760173618)
    s = addresss(a)
    logger.info(s)
