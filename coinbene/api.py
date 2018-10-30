# -*- coding: utf-8 -*-
import time
import hashlib
import requests
import json

#  此处为APIID SECRET
apiid = ''
secret = ''

#  此处为API请求地址及参数
market_url = "http://api.coinbene.com/v1/market/"
trade_url = "http://api.coinbene.com/v1/trade/"
header_dict = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",\
    "Content-Type":"application/json;charset=utf-8","Connection":"keep-alive"}

#  生成签名sign
def sign(**kwargs):
    """
    将传入的参数生成列表形式，排序后用＆拼接成字符串，用hashbli加密成生sign
    """
    sign_list = []
    for key, value in kwargs.items():
        sign_list.append("{}={}".format(key, value))
    sign_list.sort()
    sign_str = "&".join(sign_list)
    mysecret = sign_str.upper().encode()
    m = hashlib.md5()
    m.update(mysecret)
    return m.hexdigest()

#  生成时间戳
def create_timestamp():
    timestamp = int(round(time.time() * 1000))
    return timestamp

timestamp = create_timestamp()

def http_get_nosign(url):
    return http_request(url, data=None)

def http_post_sign(url,dic):
    dic["apiid"] = apiid 
    dic["secret"] = secret
    dic["timestamp"] = create_timestamp()
    mysign = sign(**dic)
    del dic['secret']
    dic['sign'] = mysign
    return http_request(url,data=dic)

def http_request(url, data) :
    if data == None:
        reponse = requests.get(url,headers=header_dict)
    else:
        reponse = requests.post(url,data=json.dumps(data),headers=header_dict) 
    try:
        if reponse.status_code == 200:
            return json.loads(reponse.text)
        else:
            return None
    except Exception as e:
        print('http failed : %s' % e)
        return None


#  获取最新价
def manbi_get_ticker(symbol):
    """
    symbol必填，为all或交易对代码:btcusdt
    """
    url = market_url + "ticker?symbol=" + str(symbol)
    return http_get_nosign(url)


#  获取挂单
def manbi_get_orderbook(symbol, depth=200):
    """
    depth为选填项，默认为200
    """
    url = market_url + "orderbook?symbol=" + symbol + "&depth=" + str(depth)
    return http_get_nosign(url)


#  获取成交记录
def manbi_get_trade(symbol, size=300):
    """
    size:获取记录数量，按照时间倒序传输。默认300
    """
    url = market_url + "trades?symbol=" + symbol + "&size=" + str(size)
    return http_get_nosign(url)


#  查询账户余额
def manbi_post_balance(dic):
    """
    以字典形式传参
    apiid:可在coinbene申请,
    secret:个人密钥(请勿透露给他人),
    timestamp:时间戳,
    account:默认为exchange，
    """
    url = trade_url + "balance"
    return http_post_sign(url, dic)


#  下单
def manbi_post_order_place(dic):
    """
    以字典形式传参
    apiid,symbol,timestamp
    type:可选 buy-limit/sell-limit
    price:购买单价
    quantity:购买数量
    """
    url = trade_url + "order/place"
    return http_post_sign(url, dic)


#  查询委托
def manbi_post_info(dic):
    """
    以字典形式传参
    apiid,timestamp,secret,orderid
    """
    url = trade_url + "order/info"
    return http_post_sign(url, dic)


#  查询当前委托
def manbi_post_open_orders(dic):
    """
    以字典形式传参
    apiid,timestamp,secret,symbol
    """
    url = trade_url + "order/open-orders"
    return http_post_sign(url, dic)


#  撤单
def manbi_post_cancel(dic):
    """
    以字典形式传参
    apiid,timestamp,secret,orderid
    """
    url = trade_url + "order/cancel"
    return http_post_sign(url, dic)
