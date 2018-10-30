# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 02:35:38 2018

@author: 60530
"""

import time
import base64
import hashlib
import requests
import json
import random
import urllib
import copy
import operator
import logging, pdb

class CoinBig():
    def __init__(self):
        self.base_url = 'https://www.coinbig.com/api/publics/v1'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        self.timeout = 10
        self.apiKey = '' 
        self.secret = ''
        
    def sign(self, params):
        params["time"] = int(round(time.time() * 1000))
        _params = copy.copy(params)
        sort_params = sorted(_params.items(), key=operator.itemgetter(0))
        #sort_params = dict(sort_params)
        paramsString = urllib.parse.urlencode(sort_params)
        #sort_params['secret_key'] = self.secret
        paramsString += '&secret_key=' + self.secret
        _sign = hashlib.md5(bytes(paramsString.encode('utf-8'))).hexdigest().upper()
        params['sign'] = _sign
        return params

    def public_request(self, method, api_url, **payload):
        try:
            r_url = self.base_url + api_url
            if method == 'POST':
                r = requests.request(method, r_url, json=payload, timeout = self.timeout, headers = self.headers)
            else:
                r = requests.request(method, r_url, params=payload, timeout = self.timeout, headers = self.headers)
            logging.info(r)
        except Exception as err:
            logging.info('%s'%(err))
            
        else:
            r.raise_for_status()

            if r.status_code == 200 and r.json()['code'] == 0:
                logging.info('%s'%(r.json()))
                return r.json()
            else:
                logging.info('%s'%(r.json()))
                    
            

    def signed_request(self, method, api_url, data = {}):
        new_data = copy.copy(data)
        new_data['apikey'] = self.apiKey
        try:
            url = self.base_url + api_url
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
            r = requests.request('POST', url, data = self.sign(new_data), headers = headers)
            
        except Exception as err:
            logging.info('err %s'%(err))
            
        else:
            r.raise_for_status()
            if r.status_code == 200 and r.json()['code'] == 0:
                logging.info('success %s'%(r.json()))
                return r.json()
            else:
                logging.info('not 200 %s'%(r.json()))           

    def list_symbol_precision(self):
        return self.public_request('GET', '/listSymbolPrecision')


    # 获取所有订单信息
    def orders_info(self, symbol, trade_type, nums=50):
        params = {'symbol':symbol,
                  'size':nums,
                  'type':trade_type}
        return self.signed_request('POST', '/orders_info', params)


    # 用户信息
    def userinfo(self):
        return self.signed_request('POST', '/userinfo')

    def cancel_order(self, order_id):
        params = {'order_id': order_id}
        return self.signed_request('POST', '/cancel_order', params)

    def ticker(self, symbol):
        return self.public_request('GET', '/ticker', symbol = symbol)

    #买卖类型: 限价单(buy/sell) 市价单(buy_market/sell_market)
    def trade(self, symbol, trade_type, price, amount):
        params = {
            'type': trade_type,
            'price': price,
            'amount': amount,
            'symbol': symbol
        }
        return self.signed_request('POST', '/trade', params)
    
    #获取深度列表
    def get_data(self, symbol):
        return self.public_request('GET', '/depthList', symbol = symbol)
    
    
  
#策略
c = CoinBig()
count=0
while 1:
    time.sleep(1)
    try:
        a=c.get_data('cb_usdt')
        buy1=float(a['data']['bids'][0]['price'])
        buy2=float(a['data']['bids'][1]['price'])
        buy3=float(a['data']['bids'][2]['price'])
        buy_amount1=float(a['data']['bids'][0]['quantity'])
        buy_amount2=float(a['data']['bids'][1]['quantity'])
        sell1=float(a['data']['asks'][0]['price'])
        sell2=float(a['data']['asks'][1]['price'])
        sell3=float(a['data']['asks'][2]['price'])
        sell_amount1=float(a['data']['asks'][0]['quantity'])
        sell_amount2=float(a['data']['asks'][1]['quantity'])
        
        b0 = c.orders_info('cb_usdt',trade_type=1)['data']['orders']
        time.sleep(1)
        b1 = c.orders_info('cb_usdt',trade_type=2)['data']['orders']
        b = b0+b1
        
        #exceed 0.1%
        if (sell1-buy1)/buy1>=0.001:
            #detect
            flag = 0
            if buy1<0.045:
                try:
                    for i in b:
                        if float(i['price'])>buy1:
                            pass
                        else:
                            if float(i['price']) < buy2:
                                c.cancel_order(i['order_id'])
                                time.sleep(1)
                            elif float(i['price'])==buy1:
                                flag = 1
                                if (buy_amount2<=5000 or float(i['price'])-buy2>0.000002) and buy_amount1 <= 800.5248:
                                    c.cancel_order(i['order_id'])
                                    time.sleep(1)
                                    flag = 0
                                elif float(i['price'])-buy2>0.000002:
                                    c.cancel_order(i['order_id'])
                                    time.sleep(1)
                                    flag = 0
                            elif float(i['price'])==buy2:
                                flag = 1
                                if buy_amount1>=5000 or (buy1-buy2<=0.000002 and buy_amount2!=800.5248)or (buy2-buy3>0.000002 and buy_amount2==800.5248):
                                    c.cancel_order(i['order_id'])
                                    time.sleep(1)
                                    flag = 0
                except Exception:
                    pass
        
                #place order
                if flag == 0:
                    a = c.get_data('cb_usdt')
                    buy1=float(a['data']['bids'][0]['price'])
                    buy2=float(a['data']['bids'][1]['price'])
                    buy_amount1=float(a['data']['bids'][0]['quantity'])
                    try:
                        if buy1-buy2>=0.000002 and buy_amount1<=5000:
                            c.trade(symbol='cb_usdt', trade_type='buy', price=round(buy2+0.000001,6), amount=800.5248) 
                        elif buy1-buy2<0.000002 and buy_amount1<=5000:
                            c.trade(symbol='cb_usdt', trade_type='buy', price=round(buy1,6), amount=800.5248)
                        else:
                            c.trade(symbol='cb_usdt', trade_type='buy', price=round(buy1+0.000001,6), amount=800.5248)
                    except Exception:
                        pass
            #挂卖单
            #检测是否已经挂单,同时撤销被埋挂单
            time.sleep(1)
            flag = 0
            if sell1>0.038:             
                try:
                    for i in b:
                        if float(i['price'])<sell1:
                            pass
                        else:
                            if float(i['price']) > sell2:
                                c.cancel_order(i['order_id'])
                            elif float(i['price'])==sell1:
                                flag = 1
                                if (sell_amount2<=5000 or sell2-float(i['price'])>0.000002) and sell_amount1 <= 801.5286:
                                    c.cancel_order(i['order_id'])
                                    flag = 0
                                elif sell2-float(i['price'])>0.000002:
                                    c.cancel_order(i['order_id'])
                                    flag = 0
                            elif float(i['price'])==sell2:
                                flag = 1
                                if sell_amount1>=5000 or (sell2-sell1<=0.000002 and sell_amount2!=801.5286) or (sell3-sell2>0.000002 and sell_amount2==801.5286):
                                    c.cancel_order(i['order_id'])
                                    flag = 0
                except Exception:
                    pass
                #place order
                if flag == 0:
                    a = c.get_data('cb_usdt')
                    sell1=float(a['data']['asks'][0]['price'])
                    sell2=float(a['data']['asks'][1]['price'])
                    sell_amount1=float(a['data']['asks'][0]['quantity'])
                    try:
                        if sell2-sell1>=0.000002 and sell_amount1<=5000:
                            sell_order=c.trade(symbol='cb_usdt', trade_type='sell', price=round(sell2-0.000001,6), amount=801.5286)
                        elif sell2-sell1<0.000002 and sell_amount1<=5000:
                            sell_order=c.trade(symbol='cb_usdt', trade_type='sell', price=round(sell1,6), amount=801.5286)
                        else:
                            sell_order=c.trade(symbol='cb_usdt', trade_type='sell', price=round(sell1-0.000001,6), amount=801.5286)
                    except Exception:
                        pass
        else:
            try:
                for i in b:
                    c.cancel_order(i['order_id'])
                    time.sleep(1)
                print('价差不够')
            except Exception:
                pass

    
    except Exception:
        try:
            for i in b:
                c.cancel_order(i['order_id'])
                time.sleep(1)
            print('出错')
        except Exception:
                pass
        continue
    
