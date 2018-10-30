import json, hashlib,struct,time,sys
import urllib.request
import urllib

class zb_api:

    def __init__(self, apikey = '5e27838f-5fe0-42b3-99b4-c800e4a8069b', secrete_key = '82e70bc8-770b-4857-95e1-eb40b8dde2f2'):
        self.mykey    = apikey
        self.mysecret = secrete_key
        self.jm = ''

    def __fill(self, value, lenght, fillByte):
        if len(value) >= lenght:
            return value
        else:
            fillSize = lenght - len(value)
        return value + chr(fillByte) * fillSize

    def __doXOr(self, s, value):
        slist = list(s.decode('utf-8'))
        for index in range(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    def __hmacSign(self, aValue, aKey):
        keyb   = struct.pack("%ds" % len(aKey), aKey.encode('utf-8'))
        value  = struct.pack("%ds" % len(aValue), aValue.encode('utf-8'))
        k_ipad = self.__doXOr(keyb, 0x36)
        k_opad = self.__doXOr(keyb, 0x5c)
        k_ipad = self.__fill(k_ipad, 64, 54)
        k_opad = self.__fill(k_opad, 64, 92)
        m = hashlib.md5()
        m.update(k_ipad.encode('utf-8'))
        m.update(value)
        dg = m.digest()
        
        m = hashlib.md5()
        m.update(k_opad.encode('utf-8'))
        subStr = dg[0:16]
        m.update(subStr)
        dg = m.hexdigest()
        return dg

    def __digest(self, aValue):
        value  = struct.pack("%ds" % len(aValue), aValue.encode('utf-8'))
        h = hashlib.sha1()
        h.update(value)
        dg = h.hexdigest()
        return dg
    
    def __public_api_call(self, path, params = ''):
        url = 'http://api.zb.com/data/v1/' + path + '?' + params
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=2)
        doc = json.loads(res.read())
        return doc

    def __api_call(self, path, params = ''):
        SHA_secret = self.__digest(self.mysecret)
        sign = self.__hmacSign(params, SHA_secret)
        self.jm = sign
        reqTime = (int)(time.time()*1000)
        params += '&sign=%s&reqTime=%d'%(sign, reqTime)

        url = 'https://trade.zb.com/api/' + path + '?' + params
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=2)
        doc = json.loads(res.read())
        return doc


    def account_info(self):
        try:
            params = "accesskey="+self.mykey+"&method=getAccountInfo"
            path = 'getAccountInfo'

            obj = self.__api_call(path, params)
            res = {}
            for i in range(len(obj['result']['coins'])):
                dic = {'available':obj['result']['coins'][i]['available'],'lock':obj['result']['coins'][i]['freez']}
                res[obj['result']['coins'][i]['key']] = dic
            return res
        except Exception as ex:
            print(sys.stderr, 'zb query_account exception,',ex)
            return None

        
    def get_depth(self, market, size = 50):
        try:
            params = "market="+market+"&size="+str(size)
            path = 'depth'
            obj = self.__public_api_call(path, params)
            return obj
        except Exception as ex:
            print(sys.stderr, 'zb get_depth exception,',ex)
            return None
        
    def limit_order(self, currency, price,amount, typ):
        if typ == 'BUY' or typ == 'buy':
            side = 1
        elif typ == 'SELL' or typ == 'sell':
            side = 0
        try:
            params_dict = {}
            params_dict['accesskey'] = self.mykey
            params_dict['amount'] = amount
            params_dict['currency'] = currency
            params_dict['method'] = 'order'
            params_dict['price'] = price
            params_dict['tradeType'] = side

            params = urllib.parse.urlencode(params_dict)
            path = 'order'
            obj = self.__api_call(path, params)
            if obj['code'] == 1000:
                return obj['id']
            else:
                return None
                print('neworder error')
        except Exception as ex:
            print(sys.stderr, 'zb zhongbi_order exception,',ex)
            return None
        
    def cancel_order(self, ord_id, currency):
        try:
            params_dict = {}
            params_dict['accesskey'] = self.mykey
            params_dict['currency'] = currency
            params_dict['id'] = ord_id
            params_dict['method'] = 'cancelOrder'

            params = urllib.parse.urlencode(params_dict)
            path = 'cancelOrder'
            obj = self.__api_call(path, params)
            return obj
        except Exception as ex:
            print(sys.stderr, 'zb cancel_order exception,',ex)
            return None    
        
    def orderinfo(self, currency,ord_id):
        try:
            params_dict = {}
            params_dict['accesskey'] = self.mykey
            params_dict['currency'] = currency
            params_dict['id'] = ord_id
            params_dict['method'] = 'getOrder'

            params = urllib.parse.urlencode(params_dict)
            path = 'getOrder'
            obj = self.__api_call(path, params)
            return obj
        except Exception as ex:
            print(sys.stderr, 'zb get_order exception,',ex)
            return None    
    
    
    def get_all_orders(self, currency, tradeType, pageIndex = 1, pageSize = 20):
        try:
            params_dict = {}
            params_dict['accesskey'] = self.mykey
            params_dict['currency'] = currency
            params_dict['method'] = 'getOrdersNew'
            params_dict['pageIndex'] = pageIndex
            params_dict['pageSize'] = pageSize
            params_dict['tradeType'] = tradeType
            params = urllib.parse.urlencode(params_dict)
            path = 'getOrdersNew'
            obj = self.__api_call(path, params)
            return obj
        except Exception as ex:
            print(sys.stderr, 'zb get_all_orders exception,',ex)
            return None
        
    def get_remain_orders(self, currency, pageIndex = 1, pageSize = 10):
        try:
            params_dict = {}
            params_dict['accesskey'] = self.mykey
            params_dict['currency'] = currency
            params_dict['method'] = 'getUnfinishedOrdersIgnoreTradeType'
            params_dict['pageIndex'] = pageIndex
            params_dict['pageSize'] = pageSize
            params = urllib.parse.urlencode(params_dict)
            path = 'getUnfinishedOrdersIgnoreTradeType'
            obj = self.__api_call(path, params)
            return obj
        except Exception as ex:
            print(sys.stderr, 'zb get_remain_orders exception,',ex)
            return None
        

        

   