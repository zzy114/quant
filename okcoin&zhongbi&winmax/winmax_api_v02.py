import json
import requests
from urllib import request ,parse
import ssl
import time
import hashlib
import random
import string

class winmax_api:
    def __init__(self,businessNo,apiSecret):
        self.businessNo = businessNo
        self.apiSecret = apiSecret
        self.url = "https://winmax.me"
        

#    def _sign(self,parms):
#        sign0 = {'apiSecret':self.apiSecret,
#                 'nonceStr':parms['nonceStr'],
#                 'timestamp':int(time.time())}
#        textmod = parse.urlencode(sign0)
#        sign = hashlib.md5()
#        sign.update(textmod.encode(encoding='utf-8'))
#        return sign.hexdigest().upper()
  
    def get_depth(self, market):    
        resource = "%s/trade/trade/trade/trade?symbol=%s&brokerId=10003"%(self.url,market)
        context = ssl._create_unverified_context()
        req = request.Request(url=resource)
        res = request.urlopen(req,context=context)
        res = res.read().decode('utf-8')
        res_dict = json.loads(res)
        res = {}
        res['bids'] = res_dict['buy']
        res['asks'] = res_dict['sell']
        return res

    def get_kline(self,market,n,typ):
        ed = int(time.time())
        be = ed - 24*60*60
        resource = "%s/dataload/kline-query/pages?startTime=%s&endTime=%s&pageSize=%s&symbol=%s&kline=%s"%(self.url,be,ed,n,market,typ)
        context = ssl._create_unverified_context()
        req = request.Request(url=resource)
        res = request.urlopen(req,context=context)
        res = res.read().decode('utf-8')
        res_dict = json.loads(res)
        return res_dict
#    def get_remain_order(self, market):
#        apikey = self.apikey
#        secretkey = self.secrete_key 
#        
#        resource = "%s/api/user/queryOrder"%self.url
#        parms = {'market':market,'apikey':apikey}
#        textmod = parse.urlencode(parms).encode(encoding='utf-8')
#
#        context = ssl._create_unverified_context()
#        req = request.Request(url=resource,data=textmod)
#        res = request.urlopen(req,context=context)
#        res = res.read().decode('utf-8')
#        res_dict = json.loads(res)
#        return res_dict
    def _dict_sort_key(self,adict):
        res = {}
        for k in sorted(adict.keys()):
            res[k] = adict[k]
        return res

    
    def account_info(self):
        ts = int(time.time())
        data = {}
        parms = {'businessNo':self.businessNo,
                 'nonceStr':'1'*32,
                 'timestamp':ts,
                 'data':data,
                 'sign':''}
        
        signal = {'apiSecret':self.apiSecret,
                 'nonceStr':'1'*32,
                 'timestamp':ts}
        signal_url = parse.urlencode(self._dict_sort_key(signal))
        sign = hashlib.md5()
        sign.update(signal_url.encode(encoding='utf-8'))
        parms['sign'] = sign.hexdigest().upper()

        resource = "%s/exchangeApi/api/asset"%self.url

        textmod = parms
        req = requests.post(url=resource,data=json.dumps(textmod))
        res_dict = json.loads(req.text)
        try:
            if res_dict['code'] == '100200':
                res = {}
                for i in range(len(res_dict['data'])):
                    dic = {'available':res_dict['data'][i]['amountAvailable'],'lock':res_dict['data'][i]['amountLock']}
                    res[res_dict['data'][i]['assetCode']] = dic
                return res
            else:
                print('winmax_account_info connect failed when time is ',ts)
        except:
            print('winmax_account_info connect failed when time is ',ts)
    
    def limit_order(self, market, price, num, side):
        
        ts = int(time.time())
        ID = str(ts)+market+side+str(round(price,0)) + ''.join(random.sample(string.ascii_letters + string.digits, 4))
        data = {'outOrderNo':ID,
                'symbol':market,
                'tradeCoinFlag':'FIXED',
                'tradeCoinType':side,
                'price':price,
                'amount':num}
        parms = {'businessNo':self.businessNo,
                 'nonceStr':'1'*32,
                 'timestamp':ts,
                 'data':data,
                 'sign':''}
        
        signal = {'apiSecret':self.apiSecret,
                 'nonceStr':'1'*32,
                 'timestamp':ts}
        signal_url = parse.urlencode(self._dict_sort_key(dict(signal,**data)))
        sign = hashlib.md5()
        sign.update(signal_url.encode(encoding='utf-8'))
        parms['sign'] = sign.hexdigest().upper()
    
        resource = "%s/exchangeApi/api/matchOrder"%self.url
        
#        textmod = parse.urlencode(parms).encode(encoding='utf-8')

#        context = ssl._create_unverified_context()
        req = requests.post(url=resource,data=json.dumps(parms))
#        res = request.urlopen(req,context=context)
#        res = res.read().decode('utf-8')
#        res_dict = json.loads(res)
        res_dict = json.loads(req.text)
#        print(ID)
        return ID

    def order_cancel(self, order_id):
        ts = int(time.time())
        
        data = {'outTradeNo':order_id}
        parms = {'businessNo':self.businessNo,
                 'nonceStr':'1'*32,
                 'timestamp':ts,
                 'data':data,
                 'sign':''}
        
        signal = {'apiSecret':self.apiSecret,
                 'nonceStr':'1'*32,
                 'timestamp':ts}
        signal_url = parse.urlencode(self._dict_sort_key(dict(signal,**data)))
        sign = hashlib.md5()
        sign.update(signal_url.encode(encoding='utf-8'))
        parms['sign'] = sign.hexdigest().upper()
    
        resource = "%s/exchangeApi/api/cancel"%self.url
        
#        textmod = parse.urlencode(parms).encode(encoding='utf-8')

#        context = ssl._create_unverified_context()
        req = requests.post(url=resource,data=json.dumps(parms))
#        res = request.urlopen(req,context=context)
#        res = res.read().decode('utf-8')
#        res_dict = json.loads(res)
        res_dict = json.loads(req.text)
        return res_dict
    
    def check_remian_order(self, market):
        ts = int(time.time())
        
        data = {'symbol':market}
        parms = {'businessNo':self.businessNo,
                 'nonceStr':'1'*32,
                 'timestamp':ts,
                 'data':data,
                 'sign':''}
        
        signal = {'apiSecret':self.apiSecret,
                 'nonceStr':'1'*32,
                 'timestamp':ts}
        signal_url = parse.urlencode(self._dict_sort_key(dict(signal,**data)))
        sign = hashlib.md5()
        sign.update(signal_url.encode(encoding='utf-8'))
        parms['sign'] = sign.hexdigest().upper()
    
        resource = "%s/exchangeApi/api/matchOrder/process"%self.url
        
#        textmod = parse.urlencode(parms).encode(encoding='utf-8')

#        context = ssl._create_unverified_context()
        req = requests.post(url=resource,data=json.dumps(parms))
#        res = request.urlopen(req,context=context)
#        res = res.read().decode('utf-8')
#        res_dict = json.loads(res)
        res_dict = json.loads(req.text)
        try:
            if res_dict['code'] == '100200':
                res = res_dict['data']
                if res == []:
                    return [{'type':None,'price':None,'id':None,'amount':None}]
                for i in range(len(res_dict['data'])):
#                    dic = {'available':res_dict['data'][i]['amountAvailable'],'lock':res_dict['data'][i]['amountLock']}
                    res[i]['amount'] = res[i]['numberOver']
                    res[i]['type'] = res[i]['tradeCoinType']
                    res[i]['id'] = res[i]['orderNo']
                return res
            else:
                print('check_remian_order connect failed when time is ',ts)
        except:
            print('check_remian_order connect failed when time is ',ts)
   
    def is_cancel(self, order_id):
        ts = int(time.time())
        data = {'outTradeNo':str(order_id)}
        parms = {'businessNo':self.businessNo,
                 'nonceStr':'1'*32,
                 'timestamp':ts,
                 'data':data,
                 'sign':''}
        
        signal = {'apiSecret':self.apiSecret,
                 'nonceStr':'1'*32,
                 'timestamp':ts}
        signal_url = parse.urlencode(self._dict_sort_key(dict(signal,**data)))
        sign = hashlib.md5()
        sign.update(signal_url.encode(encoding='utf-8'))
        parms['sign'] = sign.hexdigest().upper()
    
        resource = "%s/exchangeApi/api/orderqueryByH"%self.url
        
#        textmod = parse.urlencode(parms).encode(encoding='utf-8')

#        context = ssl._create_unverified_context()
        req = requests.post(url=resource,data=json.dumps(parms))
#        res = request.urlopen(req,context=context)
#        res = res.read().decode('utf-8')
#        res_dict = json.loads(res)
        res_dict = json.loads(req.text)
        try:
            if res_dict['code'] == '100200':
                if res_dict['data']['tradeCoinStatus'] in ['UNQUEUE','WAITING']:
                    return True
                else:
                    print(res_dict)
                    return False
            else:
                print('is_cancel connect failed when time is ',ts)
                return False
        except:
            print('is_cancel connect failed when time is ',ts)
            return False
'''

    def get_trade_ticker(self, market):
        
        resource = "%s/api/ticker/getTicker"%self.url
        parms = {'market':market}
        
        textmod = parse.urlencode(parms).encode(encoding='utf-8')

        context = ssl._create_unverified_context()
        req = request.Request(url=resource,data=textmod)
        res = request.urlopen(req,context=context)
        res = res.read().decode('utf-8')
        res_dict = json.loads(res)
        
        return res_dict
'''
        
if __name__=='__main__':
    wkt_t = winmax_api('ysjj1132','ysjj11321qaz')
    wkt_t.account_info()
    wkt_t.get_depth('UDC_LTC')
#    wkt_t.limit_order('UDC_ETH', 502, 1, 'BUY')
#    ss = wkt_t.order_cancel('a23')
#    
#    print(ss)
        




