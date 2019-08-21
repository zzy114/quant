import base64
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests
import time

# type
ACCESS_KEY = "5d3ebe4dc29cc67e5dfa8636"
SECRET_KEY = "da220752-919f-48e8-bed8-93b4c3707fe3"

# new
ACCESS_KEY = "5d357e7f38300c2e55508bae"
SECRET_KEY = "9ef95869-63b1-43ae-ae17-9b1efe372543"



def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    response = requests.get(url, postdata, headers=headers, timeout=5)
    # print(response.json())
    try:

        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        print("httpGet failed, detail is:%s,%s" % (response.text, e))
        return


def http_post_request(url, params, add_to_headers=None):
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = json.dumps(params)
    response = requests.post(url, postdata, headers=headers, timeout=200)
    try:

        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        print("httpPost failed, detail is:%s,%s" % (response.text, e))
        return



def get_ticker(symbol):
    """
    :param symbol:
    :return:
    """
    params = {'symbol': symbol}

    url = 'https://api.kumex.com/api/v1/ticker'
    return http_get_request(url, params)

def header(str_to_sign,now):
    api_key = ACCESS_KEY
    api_secret = SECRET_KEY
    api_passphrase = "134679258"
    # api_passphrase = '738291465'
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json"  # specifying content type or using json=data in request
    }
    return headers

def send_order(oid, price, side, size):
    now = int(time.time() * 1000)
    url = 'https://api.kumex.com/api/v1/orders'
    data = {"clientOid": oid,
            "reduceOnly": False,
            "closeOrder": False,
            "forceHold": False,
            "hidden": False,
            "iceberg": False,
            "leverage": 20,
            "postOnly": False,
            "price": str(price),
            "remark": "remark",
            "side": side,
            "size": size,
            "stop": "",
            "stopPrice": 0,
            "stopPriceType": "",
            "symbol": "XBTUSDM",
            "timeInForce": "",
            "type": "limit",
            "visibleSize": 0
            }

    data_json = json.dumps(data)
    str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json
    headers = header(str_to_sign, now)
    response = requests.request('post', url, headers=headers, data=data_json)
    return response.json()

def cancel_orders():
    url = 'https://api.kumex.com/api/v1/orders?symbol=XBTUSDM'
    now = int(time.time() * 1000)
    # data = {"cancelledOrderIds": oid}
    #
    # data_json = json.dumps(data)
    str_to_sign = str(now) + 'DELETE' + '/api/v1/orders?symbol=XBTUSDM'
    headers = header(str_to_sign, now)
    response = requests.request('delete', url, headers=headers)

    return response.json()

def cancel_order(oid):
    url = 'https://api.kumex.com/api/v1/orders/'+oid
    now = int(time.time() * 1000)
    # data = {"cancelledOrderIds": oid}
    #
    # data_json = json.dumps(data)
    str_to_sign = str(now) + 'DELETE' + '/api/v1/orders/'+oid
    headers = header(str_to_sign, now)
    response = requests.request('delete', url, headers=headers)

    return response.json()


def fetch_order(oid):
    url = 'https://api.kumex.com/api/v1/orders/'+oid
    now = int(time.time() * 1000)
    # data = {"id": oid}
    # data_json = json.dumps(data)
    str_to_sign = str(now) + 'GET' + '/api/v1/orders/'+oid
    headers = header(str_to_sign, now)
    response = requests.request('get', url, headers=headers)
    return response.json()


def fetch_orders():
    url = 'https://api.kumex.com/api/v1/orders?status=active'
    now = int(time.time() * 1000)
    # data = {"id": oid}
    # data_json = json.dumps(data)
    str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
    headers = header(str_to_sign, now)
    response = requests.request('get', url, headers=headers)
    return response.json()


def get_position():
    url = 'https://api.kumex.com/api/v1/position?symbol=XBTUSDM'
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + '/api/v1/position?symbol=XBTUSDM'

    headers = header(str_to_sign, now)
    response = requests.request('get', url, headers=headers)

    return response.json()


def get_index(symbol):
    """
    :param symbol:
    :return:
    """
    params = {'symbol': symbol}

    url = 'https://api.kumex.com/api/v1/mark-price/XBTUSDM/current'
    return http_get_request(url, params)


def get_account():
    url = 'https://api.kumex.com/api/v1/account-overview'
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + '/api/v1/account-overview'

    headers = header(str_to_sign, now)
    response = requests.request('get', url, headers=headers)

    return response.json()


old_ask = 0
old_bid = 0
# 1两面摆单，2买单成交，卖单只挂卖一 3卖单成交，买单只挂买一
stage = 1
run = 1
while run:
    try:
        try:
            position = get_position()
            position = position['data']['currentQty']
            if position > 0:
                stage = 2
            elif position < 0:
                stage = 3
            else:
                stage = 1

        except KeyError:
            pass

        res = get_ticker('XBTUSDM')
        ask = float(res['data']['bestAskPrice'])
        bid = float(res['data']['bestBidPrice'])

        if ask != old_ask:
            old_ask = ask
            try:
                cancel_order(sell_id)
            except BaseException:
                pass
            if stage == 2:
                sell = send_order(str(int(time.time() * 20000)), ask, 'sell', position)

            elif stage == 1 or stage == 0:
                sell = send_order(str(int(time.time() * 20000)), ask + 15, 'sell', 150500)
            try:
                sell_id = sell['data']['orderId']

            except BaseException:
                pass

        if bid != old_bid:
            old_bid = bid
            try:
                cancel_order(buy_id)
            except BaseException:
                pass

            if stage == 3:
                buy = send_order(str(int(time.time() * 20000)), bid, 'buy', -position)
            elif stage == 1 or stage == 0:
                buy = send_order(str(int(time.time() * 20000)), bid - 15, 'buy', 150500)
            try:
                buy_id = buy['data']['orderId']
            except BaseException:
                pass

        time.sleep(2.5)

    except BaseException:
        time.sleep(30)



