import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('XBTUSD_1minute_bar_2018.csv')

datetime = df['timestamp']
datetime = pd.to_datetime(datetime)
del df['timestamp']

data = df.values.astype(None)

for j in range(data.shape[1]):
    if j < data.shape[1]:
        for i in range(data.shape[0]):
            if np.isnan(data[i, j]):
                data[i, j] = data[i - 1, 3]
    else:
        for i in range(data.shape[0]):
            if np.isnan(data[i, j]):
                data[i, j] = 0

lth = len(datetime)
fee = 5 / 10000
profit = np.full((lth, 1), 0.00, dtype=float)  # 创建利润记录矩阵
holding = np.full((lth, 1), 0.00, dtype=float)  # 创建持仓记录矩阵
entryprice = np.full((lth, 1), 0.00, dtype=float)  # 创建买入价格记录矩阵

Multipier = 10  # 合约乘数
slip = 0  # 滑点
tradetimes = 0  # 交易次数

Close = data[:, 3]  # 收盘价
Close.shape = (lth, 1)

## 因子计算
rtn = np.concatenate((np.full((1, 1), np.nan), Close[1:] / Close[:-1] - 1))
boll_ma = np.full((lth, 1), np.nan)
boll_std = np.full((lth, 1), np.nan)
n_windows = 60
for i in range(n_windows - 1, lth):
    boll_ma[i, 0] = np.mean(rtn[i - n_windows + 1:i + 1, 0])
    boll_std[i, 0] = np.std(rtn[i - n_windows + 1:i + 1, 0], ddof=1)

k_start = 5
k_stop = 0
boll_up_1 = boll_ma + k_start * boll_std
boll_up_2 = boll_ma + k_stop * boll_std
boll_down_1 = boll_ma - k_start * boll_std
boll_down_2 = boll_ma - k_stop * boll_std

## 开始回测
for i in range(1, lth):
    holding[i] = holding[i - 1]
    entryprice[i] = holding[i - 1]

    if i > n_windows - 2:
        buy = rtn[i - 1, 0] > boll_down_1[i - 1, 0] and rtn[i, 0] <= boll_down_1[i, 0]  # 开多
        sellshort = rtn[i - 1, 0] < boll_up_1[i - 1, 0] and rtn[i, 0] >= boll_up_1[i, 0]  # 开空
        sell = rtn[i - 1, 0] < boll_down_2[i - 1, 0] and rtn[i, 0] >= boll_down_2[i, 0]  # 平多
        buytocover = rtn[i - 1, 0] > boll_up_2[i - 1, 0] and rtn[i, 0] <= boll_up_2[i, 0]  # 平空

        if (buytocover and holding[i] < -0.5) or (sell and holding[i] > 0.5):  # 平仓利润计算
            profit[i] = profit[i] - Close[i] * fee - slip * Multipier
            holding[i] = 0
            tradetimes = tradetimes + 1

        if sellshort and holding[i] > -0.5:  # 开空利润计算
            if holding[i] > 0.5:  # 先平多再开空
                profit[i] = profit[i] - Close[i] * fee - slip * Multipier
                tradetimes = tradetimes + 1
            entryprice[i] = Close[i]
            profit[i] = profit[i] - Close[i] * fee - slip * Multipier
            holding[i] = -1

        if buy and holding[i] < 0.5:  # 开多利润计算
            if holding[i] < -0.5:  # 先平空再开多
                profit[i] = profit[i] - Close[i] * fee - slip * Multipier
                tradetimes = tradetimes + 1
            entryprice[i] = Close[i]
            profit[i] = profit[i] - Close[i] * fee - slip * Multipier
            holding[i] = 1

        if holding[i - 1] > 0.5:  # 持有多仓时利润计算
            profit[i] = profit[i] + (Close[i] - Close[i - 1]) * Multipier

        if holding[i - 1] < -0.5:  # 持有空仓时利润计算
            profit[i] = profit[i] + (Close[i - 1] - Close[i]) * Multipier

sumprofit = np.cumsum(profit)  # 累积利润计算
sumprofit.shape = (lth, 1)

## 计算最大回撤
mb = np.full((lth, 1), np.nan)
highestprofit = 0
maxback = 0
for i in range(lth):
    highestprofit = np.max([highestprofit, sumprofit[i, 0]])
    maxback = np.max([maxback, highestprofit - sumprofit[i, 0]])
    mb[i, 0] = maxback

## 计算收益风险比
dt = pd.concat(
    [datetime.dt.year, datetime.dt.month, datetime.dt.day, datetime.dt.hour, datetime.dt.minute, datetime.dt.second],
    axis=1).values.astype(None)
timenum = dt[-1, :] - dt[0, :]
income_risk = sumprofit[-1] / maxback / (
        timenum[0] + timenum[1] / 12 + timenum[2] / 12 / 31 + timenum[3] / 12 / 31 / 12 + timenum[
    4] / 12 / 31 / 12 / 60 + timenum[5] / 12 / 31 / 12 / 60 / 60)

plt.subplot(211)
plt.plot(datetime, sumprofit)
plt.legend(
    ['income_rick=' + str(income_risk) + '  commission=' + str(fee) + '  slip=' + str(slip) + '  Multipier=' + str(
        Multipier)],
    loc='upper left')
plt.title('rtn_bollband strategy')
plt.subplot(212)
plt.plot(datetime, mb)
plt.legend(
    ['maxdrawback'],
    loc='upper left')
plt.show()
