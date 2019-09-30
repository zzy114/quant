import pandas as pd
from zzy_lib import *
import matplotlib.pyplot as plt
import statsmodels.api as sm

df = pd.read_csv(r'C:\Users\60530\Desktop\量化交易\RGF\高频因子研究测试题\au1912_20190924.csv', engine='python')
df = df.iloc[1:, :]

datetime = df.apply(lambda x: str(x['Date']) + x['Time'], axis=1)
datetime = pd.to_datetime(datetime, format='%Y%m%d%H:%M:%S.%f')

# FairPrice = (BidPrice * AskSize + AskPrice * BidSize) / (BidSize + AskSize)
FairPrice = df.apply(lambda x: ((x['BidPrice1'] * x['AskVolume1'] + (x['AskPrice1'] * x['BidVolume1'])) /
                                (x['BidVolume1'] + x['AskVolume1'])), axis=1)

# OIR(Order Imbalance Ratio) = (BidSize - AskSize) / (BidSize+AskSize)
OIR = df.apply(lambda x: ((x['BidVolume1'] - x['AskVolume1']) / (x['BidVolume1'] + x['AskVolume1'])), axis=1)

length = df.shape[0]
# 标记买卖的止盈止损结果
buy, sell = label(FairPrice, length)

ret = FairPrice.pct_change()
# 查看异常值
ret1 = ret[1:].reindex(ret[1:].abs().sort_values(ascending=False).index)*1000
# 去除两个异常值
ret2 = ret.drop(index=ret1.index[:2])[1:]
OIR2 = OIR.drop(index=ret1.index[:2])[1:]
# datetime2 = datetime.drop(index=ret1.index[:2])[1:]

# OLS拟合
X = sm.add_constant(OIR2)
result = (sm.OLS(ret2.astype(float), X.astype(float))).fit()
# result.summary()显示R^2小，拟合效果差
b = result.params['const']
a = result.params[0]

# 作图
# y_fitted = result.fittedvalues
# plt.figure(figsize=(10, 5))
# plt.plot(datetime2, ret2)
# plt.plot(datetime2, y_fitted)
# plt.show()

# 因子生成
# OIR = OIR.values.astype(None)
factor = a*OIR + b
buy_factor = factor.apply(lambda x: 1 if x >= 0 else 0)
sell_factor = factor.apply(lambda x: 1 if x <= 0 else 0)

# 收益计算
buy_factor1 = buy_factor.values.astype(None)
buy_profit = buy_factor1 * buy.flatten()

sell_factor1 = sell_factor.values.astype(None)
sell_profit = sell_factor1 * sell.flatten()

profit = buy_profit + sell_profit
# 胜率计算
tp_times = sum(profit == 1)
sl_times = sum(profit == -3)
win_ratio = tp_times / (tp_times + sl_times)

# sumprofit = np.sum(profit)
sumprofit = np.cumsum(profit)

sumprofit.shape = (length, 1)

# 计算最大回撤
mb = np.full((length, 1), np.nan)
highestprofit = 0
maxback = 0
for i in range(length):
    highestprofit = np.max([highestprofit, sumprofit[i, 0]])
    maxback = np.max([maxback, highestprofit - sumprofit[i, 0]])
    mb[i, 0] = maxback

# 计算夏普比率
sharpe_ratio = np.sqrt(length) * profit.mean() / profit.std()

# 作图
plt.figure(figsize=(15, 5))
plt.plot(sumprofit)
plt.title('au_strategy')

