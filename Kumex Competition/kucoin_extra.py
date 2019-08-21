import base64
import uuid
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests
import time

# zbw
ACCESS_KEY = "5d2c45c938300c2e554690fb"
SECRET_KEY = "1db09110-3f4f-4d44-b470-fdaffb2b359d"

# 605302155
# ACCESS_KEY = "5d2c44d338300c2e55468ff1"
# SECRET_KEY = "5e499845-bfb3-42c1-8266-a9f70b93cf66"

# zhangzhiyang16
# ACCESS_KEY = "5d2c418e134ab77425820618"
# SECRET_KEY = "c9e9019e-8488-4a85-86f2-aa3c85488086"

# new
# ACCESS_KEY = "5d2c5750c29cc610bed70488"
# SECRET_KEY = "0bca1fee-b6df-40ab-b805-65f71b8c2562"

# zhangzhiyang13
ACCESS_KEY = "5d3579fb134ab774258bf6c0"
SECRET_KEY = "49dded3e-a5e8-4427-a27e-799ee8af052c"

# new
ACCESS_KEY = "5d357e7f38300c2e55508bae"
SECRET_KEY = "9ef95869-63b1-43ae-ae17-9b1efe372543"

# zbw
ACCESS_KEY = "5d3586bb134ab774258c069d"
SECRET_KEY = "7bde4f29-a0f4-44b3-8293-2b3c160352f2"

# type
ACCESS_KEY = "5d3ebe4dc29cc67e5dfa8636"
SECRET_KEY = "da220752-919f-48e8-bed8-93b4c3707fe3"


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
    api_passphrase = '738291465'
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


old_ask = 0
old_bid = 0
# 1两面摆单，2买单成交，卖单只挂卖一 3卖单成交，买单只挂买一
stage = 1
run = 1

sell_id = [0, 0, 0, 0, 0, 0, 0, 0]
buy_id = [0, 0, 0, 0, 0, 0, 0, 0]

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

            for i in range(8):
                try:
                    cancel_order(sell_id[i])
                except BaseException:
                    pass
                if i != 7 and stage != 3:
                    sell = send_order(str(uuid.uuid4()), ask + 3 + i, 'sell', 10000 + 3500*i)
                if stage == 2 and i == 7:
                    sell = send_order(str(int(time.time() * 20000)), ask, 'sell', position)
                try:
                    sell_id[i] = sell['data']['orderId']
                    time.sleep(0.05)

                except BaseException:
                    pass

        if bid != old_bid:
            old_bid = bid

            for i in range(8):
                try:
                    cancel_order(buy_id[i])

                except BaseException:
                    pass
                if i != 7 and stage != 2:
                    buy = send_order(str(uuid.uuid4()), bid - 3 - i, 'buy', 10000 + 3500*i)

                if stage == 3 and i == 7:
                    buy = send_order(str(int(time.time() * 20000)), bid, 'buy', -position)
                try:
                    buy_id[i] = buy['data']['orderId']
                    time.sleep(0.05)
                except BaseException:
                    pass

        time.sleep(2.5)

    except BaseException:
        time.sleep(30)


