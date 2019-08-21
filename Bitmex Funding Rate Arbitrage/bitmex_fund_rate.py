# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 13:28:41 2019

@author: rgf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(r'C:\Users\60530\Desktop\Funding History (symbol=XBTUSD) 2019-6-11.csv')
df = df.iloc[::-1].reset_index()
rate = df['fundingRate']

datetime = df['timestamp']
datetime = pd.to_datetime(datetime)
del df['timestamp']



lth = len(datetime)

profit = np.full((lth, 1), 0.00, dtype=float)  # 创建利润记录矩阵
holding = np.full((lth, 1), 0.00, dtype=float)  # 创建持仓记录矩阵
holding[0] = 3
profit[0] = 0

# entryprice = np.full((lth, 1), 0.00, dtype=float)  # 创建买入价格记录矩阵

# Multipier = 10  # 合约乘数
# slip = 0  # 滑点
# tradetimes = 0  # 交易次数

# Close = data[:, 3]  # 收盘价
# Close.shape = (lth, 1)

# price= 0 #记录开仓价格
# buy = 0  # 开多
# sellshort = 0  # 开空
# sell = 0  # 平多
# buytocover = 0  # 平空
# count = 0 #反手次数
# max_count = 0 #最大反手次数

## 开始回测
for i in range(1, lth):
    profit[i] = profit[i-1]
    holding[i] = holding[i - 1]
    if rate[i-1] < 0 and rate[i] > 0:
        profit[i] = profit[i-1]-(1 + profit[i-1])*0.75/1000-1
    if rate[i-1] < 0 and rate[i] < 0:
        profit[i] = (1 + rate[i]-1/1000)*(1 + profit[i-1])-1


    if rate[i] > 0:
        if rate[i] < 0.00017:
            profit[i] = (1 + rate[i])*(1 + profit[i])-1
        else:
            trade_amount = abs(4-holding[i])
            profit[i] = profit[i] - trade_amount/4/1000-1

    if rate[i] < 0:
        if rate[i] < 0.00017:
            profit[i] = (1 + rate[i])*(1 + profit[i])-1
        else:
            trade_amount = abs(4-holding[i])
            profit[i] = profit[i] - trade_amount/4/1000-1


    elif rate[i] <= 0 and rate[i-1] > 0:
        profit[i] = profit[i - 1] - (1 + profit[i - 1]) * 0.75 / 1000
        profit[i] = (1 + rate[i]-1/1000)*(1 + profit[i])-1



## 计算收益风险比
# dt = pd.concat(
#     [datetime.dt.year, datetime.dt.month, datetime.dt.day, datetime.dt.hour, datetime.dt.minute, datetime.dt.second],
#     axis=1).values.astype(None)
# timenum = dt[-1, :] - dt[0, :]
# income_risk = sumprofit[-1] / maxback / (
#         timenum[0] + timenum[1] / 12 + timenum[2] / 12 / 31 + timenum[3] / 12 / 31 / 12 + timenum[
#     4] / 12 / 31 / 12 / 60 + timenum[5] / 12 / 31 / 12 / 60 / 60)
#
#
plt.figure(figsize=(15, 5))
plt.plot(datetime, profit)
plt.legend(
    ['commission=0.001'],
    loc='upper left')
plt.title('Profit of Bitmex Funding Rate Arbitrage')
plt.show()


plt.figure(figsize=(10, 5))
plt.plot(datetime, mb)
plt.legend(
    ['maxdrawback'],
    loc='upper left')
plt.show()


