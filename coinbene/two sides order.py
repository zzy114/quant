# -*- coding: utf-8 -*-
from api import *

#策略
count=0
while 1:
    try:
        a = get_orderbook('goteth',3)
        buy1=a['orderbook']['bids'][0]['price']
        buy2=a['orderbook']['bids'][1]['price']
        buy3=a['orderbook']['bids'][2]['price']
        buy_amount1=a['orderbook']['bids'][0]['quantity']
        buy_amount2=a['orderbook']['bids'][1]['quantity']
        sell1=a['orderbook']['asks'][0]['price']
        sell2=a['orderbook']['asks'][1]['price']
        sell3=a['orderbook']['asks'][2]['price']
        sell_amount1=a['orderbook']['asks'][0]['quantity']
        sell_amount2=a['orderbook']['asks'][1]['quantity']
        #如果买单卖单价差超过1.5%
        if (sell1-buy1)/buy1>=0.015:
            b = post_open_orders({'symbol':'goteth'})
            #挂买单
            #检测是否已经挂单,同时撤销被埋挂单
            flag = 0
            try:
                for i in b['orders']['result']:
                    if float(i['price'])>buy1:
                        pass
                    else:
                        if float(i['price']) < buy2:
                            post_cancel({"orderid":i['orderid']})
                        elif float(i['price'])==buy1:
                            flag = 1
                            if (buy_amount2<=1000 or float(i['price'])-buy2>0.000002) and buy_amount1 <= 305.18:
                                post_cancel({"orderid":i['orderid']})
                                flag = 0
                            elif float(i['price'])-buy2>0.000002:
                                post_cancel({"orderid":i['orderid']})
                                flag = 0
                        elif float(i['price'])==buy2:
                            flag = 1
                            if buy_amount1>=1000 or (buy1-buy2<=0.000002 and buy_amount2!=305.18)or (buy2-buy3>0.000002 and buy_amount2==305.18):
                                post_cancel({"orderid":i['orderid']})
                                flag = 0
            except Exception:
                pass

            #未挂单且持仓未达上限
            c = post_balance({"account":"exchange"})
            balance = float(c['balance'][103]['available'])
            if flag == 0:
                a = get_orderbook('goteth',3)
                buy1=a['orderbook']['bids'][0]['price']
                buy2=a['orderbook']['bids'][1]['price']
                buy_amount1=a['orderbook']['bids'][0]['quantity']
                try:
                    if buy1-buy2>=0.000002 and buy_amount1<=1000:
                        buy_order = post_order_place({'symbol':'goteth',"type":"buy-limit","price":round(buy2+0.000001,6),"quantity":305.18,"symbol":"goteth"})
                    elif buy1-buy2<0.000002 and buy_amount1<=1000:
                        buy_order = post_order_place({'symbol':'goteth',"type":"buy-limit","price":round(buy1,6),"quantity":305.18,"symbol":"goteth"})
                    else:
                        buy_order = post_order_place({'symbol':'goteth',"type":"buy-limit","price":round(buy1+0.000001,6),"quantity":305.18,"symbol":"goteth"})
                except Exception:
                    pass
            #挂卖单
            #检测是否已经挂单,同时撤销被埋挂单
            flag = 0
            try:
                for i in b['orders']['result']:
                    if float(i['price'])<sell1:
                        pass
                    else:
                        if float(i['price']) > sell2:
                            post_cancel({"orderid":i['orderid']})
                        elif float(i['price'])==sell1:
                            flag = 1
                            if (sell_amount2<=1000 or sell2-float(i['price'])>0.000002) and sell_amount1 <= 305.18:
                                post_cancel({"orderid":i['orderid']})
                                flag = 0
                            elif sell2-float(i['price'])>0.000002:
                                post_cancel({"orderid":i['orderid']})
                                flag = 0
                        elif float(i['price'])==sell2:
                            flag = 1
                            if sell_amount1>=1000 or (sell2-sell1<=0.000002 and sell_amount2!=305.18) or (sell3-sell2>0.000002 and sell_amount2==305.18):
                                post_cancel({"orderid":i['orderid']})
                                flag = 0
            except Exception:
                pass
            #未挂单且持仓未达上限
            c = post_balance({"account":"exchange"})
            balance = float(c['balance'][103]['available'])
            if flag == 0:
                a = get_orderbook('goteth',3)
                sell1=a['orderbook']['asks'][0]['price']
                sell2=a['orderbook']['asks'][1]['price']
                sell_amount1=a['orderbook']['asks'][0]['quantity']
                try:
                    if sell2-sell1>=0.000002 and sell_amount1<=1000:
                        sell_order = post_order_place({'symbol':'goteth',"type":"sell-limit","price":round(sell2-0.000001,6),"quantity":305.18,"symbol":"goteth"})
                    elif sell2-sell1<0.000002 and sell_amount1<=1000:
                        sell_order = post_order_place({'symbol':'goteth',"type":"sell-limit","price":round(sell1,6),"quantity":305.18,"symbol":"goteth"})
                    else:
                        sell_order = post_order_place({'symbol':'goteth',"type":"sell-limit","price":round(sell1-0.000001,6),"quantity":305.18,"symbol":"goteth"})
                except Exception:
                    pass
        else:
            try:
                for i in b['orders']['result']:
                    post_cancel({"orderid":i['orderid']})
                print('价差不够')
            except Exception:
                pass
        
        time.sleep(2)
        count+=1
        if count==1:
            temp = [sell1,buy1]
        if count==60:
            #浮动超过4.5%，取消所有挂单，程序停止1000秒
            a2 = get_orderbook('goteth',3)
            if a2['orderbook']['asks'][0]['price']/temp[0]>=1.045 or a2['orderbook']['bids'][0]['price']/temp[1]<=0.955:
                for i in b['orders']['result']:
                    post_cancel({"orderid":i['orderid']})
                print('高比例浮动')
                time.sleep(1000)
            count=0
        
    except Exception:
        try:
            for i in b['orders']['result']:
                post_cancel({"orderid":i['orderid']})
            print('出错')
        except Exception:
                pass
        continue

