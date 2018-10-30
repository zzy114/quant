# -*- coding: utf-8 -*-

from api import *

#策略
count=0
while 1:
    try:
        a = get_orderbook('trxusdt',3)
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
        limit = 0.0325
        #如果买单卖单价差超过1.5%
        if (sell1-buy1)/buy1>=0.015:
            b = post_open_orders({'symbol':'trxusdt'})
            #挂买单
            #检测是否已经挂单,同时撤销被埋挂单
            flag = 0
            try:
                if buy1< limit:  
                    for i in b['orders']['result']:
                        if float(i['price'])>buy1:
                            pass
                        else:
                            if float(i['price']) < buy2:
                                post_cancel({"orderid":i['orderid']})
                            elif float(i['price'])==buy1:
                                flag = 1
                                if (buy_amount2<=300 or float(i['price'])-buy2>0.00011) and buy_amount1 <= 740.08:
                                    post_cancel({"orderid":i['orderid']})
                                    flag = 0
                                elif float(i['price'])-buy2>0.001:
                                    post_cancel({"orderid":i['orderid']})
                                    flag = 0
                            elif float(i['price'])==buy2:
                                flag = 1
                                if buy_amount1>=300 or (buy1-buy2<=0.0001 and buy_amount2!=740.08) or (buy2-buy3>0.00011 and buy_amount2==740.08):
                                    post_cancel({"orderid":i['orderid']})
                                    flag = 0
                else:
                    for i in b['orders']['result']:
                        if float(i['price']) == limit:
                            flag=1
            except:
                pass

            #未挂单且持仓未达上限
            c = post_balance({"account":"exchange"})
            balance = float(c['balance'][68]['available'])
            if flag == 0 and balance <= 4000:
                a = get_orderbook('trxusdt',3)
                buy1=a['orderbook']['bids'][0]['price']
                buy2=a['orderbook']['bids'][1]['price']
                buy_amount1=a['orderbook']['bids'][0]['quantity']
                try:
                    if buy1<limit:                 
                        if buy1-buy2>=0.001 and buy_amount1<=300:
                            buy_order = post_order_place({'symbol':'trxusdt',"type":"buy-limit","price":round(buy2+0.0001,4),"quantity":740.08,"symbol":"trxusdt"})
                        elif buy1-buy2<0.001 and buy_amount1<=300:
                            buy_order = post_order_place({'symbol':'trxusdt',"type":"buy-limit","price":round(buy1,4),"quantity":740.08,"symbol":"trxusdt"})
                        else:
                            buy_order = post_order_place({'symbol':'trxusdt',"type":"buy-limit","price":round(buy1+0.0001,4),"quantity":740.08,"symbol":"trxusdt"})
                    else:
                        buy_order = post_order_place({'symbol':'trxusdt',"type":"buy-limit","price":limit,"quantity":740.08,"symbol":"trxusdt"})
                except:
                    pass
            #挂卖单
            #检测是否已经挂单,同时撤销被埋挂单
            flag = 0
            try:
                if sell1>limit+0.0005:
                    for i in b['orders']['result']:
                        if float(i['price'])<sell1:
                            pass
                        else:                               
                            if float(i['price']) > sell2:
                                post_cancel({"orderid":i['orderid']})
                            elif float(i['price'])==sell1:
                                flag = 1
                                if (sell_amount2<=300 or sell2-float(i['price'])>0.00011) and sell_amount1 <= 740.08:
                                    post_cancel({"orderid":i['orderid']})
                                    flag = 0
                                elif sell2-float(i['price'])>0.001:
                                    post_cancel({"orderid":i['orderid']})
                                    flag = 0
                            elif float(i['price'])==sell2:
                                flag = 1
                                if sell_amount1>=300 or (sell2-sell1<=0.0001 and sell_amount2==740.08) or (sell3-sell2>0.00011 and sell_amount2==740.08):
                                    post_cancel({"orderid":i['orderid']})
                                    flag = 0
                else:
                    for i in b['orders']['result']:
                        if float(i['price']) == (limit+0.0005):
                            flag=1
            except:
                pass
            #未挂单且持仓未达上限
            c = post_balance({"account":"exchange"})
            balance = float(c['balance'][68]['available'])
            if flag == 0 and balance >= 100:
                a = get_orderbook('trxusdt',3)
                sell1=a['orderbook']['asks'][0]['price']
                sell2=a['orderbook']['asks'][1]['price']
                sell_amount1=a['orderbook']['asks'][0]['quantity']
                try:
                    if sell1>limit+0.0005:     
                        if sell2-sell1>=0.001 and sell_amount1<=300:
                            sell_order = post_order_place({'symbol':'trxusdt',"type":"sell-limit","price":round(sell2-0.0001,4),"quantity":740.08,"symbol":"trxusdt"})
                        elif sell2-sell1<0.001 and sell_amount1<=300:
                            sell_order = post_order_place({'symbol':'trxusdt',"type":"sell-limit","price":round(sell1,4),"quantity":740.08,"symbol":"trxusdt"})
                        else:
                            sell_order = post_order_place({'symbol':'trxusdt',"type":"sell-limit","price":round(sell1-0.0001,4),"quantity":740.08,"symbol":"trxusdt"})
                    else:
                        sell_order = post_order_place({'symbol':'trxusdt',"type":"sell-limit","price":limit+0.0005,"quantity":740.08,"symbol":"trxusdt"})
                except:
                    pass
        else:
            try:
                for i in b['orders']['result']:
                    post_cancel({"orderid":i['orderid']})
                print('价差不够')
            except:
                pass
        
        time.sleep(2)
        count+=1
        if count==1:
            temp = [sell1,buy1]
        if count==60:
            #浮动超过2.5%，取消所有挂单，程序停止1000秒
            a2 = get_orderbook('trxusdt',3)
            if a2['orderbook']['asks'][0]['price']/temp[0]>=1.075 or a2['orderbook']['bids'][0]['price']/temp[1]<=0.925:
                for i in b['orders']['result']:
                    post_cancel({"orderid":i['orderid']})
                print('高比例浮动')
                time.sleep(1000)
            count=0
        
    except:
        try:
            for i in b['orders']['result']:
                post_cancel({"orderid":i['orderid']})
            print('出错')
        except:
                pass
        continue