# Here you can
# 1. import necessary python packages for your strategy
# 2. Load your own facility files containing functions, trained models, extra data, etc for later use
# 3. Set some global constants
# Note:
# 1. You should put your facility files in the same folder as this strategy.py file
# 2. When load files, ALWAYS use relative path such as "data/facility.pickle"
# DO NOT use absolute path such as "C:/Users/Peter/Documents/project/data/facility.pickle"
import numpy as np
import h5py
from pandas import DataFrame
import statsmodels.api as sm
#import matplotlib.pyplot as plt


assert_BCH = 0  
assert_BTC = 1
assert_ETH = 2  
assert_LTC = 3
    
exchange = [1,48]

#读取上一星期的最后720个数据
format1_dir = r'data/data_format1_20181021_20181028.h5'
format2_dir = r'data/data_format2_20181021_20181028.h5'
format1 = h5py.File(format1_dir, mode='r')
format2 = h5py.File(format2_dir, mode='r')
assets = list(format1.keys())
keys = list(format2.keys())
keys.reverse()

price_list = DataFrame(columns = ['BCH','BTC','ETH','LTC'])
for index,value in enumerate(keys):
    if index > 719:
        break
    data_cur_min = format2[value][[assert_BCH,assert_BTC,assert_ETH,assert_LTC],:]
    price_list.loc[index,'BCH'] = np.mean(data_cur_min[0,:4])
    price_list.loc[index,'BTC'] = np.mean(data_cur_min[1,:4])
    price_list.loc[index,'ETH'] = np.mean(data_cur_min[2,:4])
    price_list.loc[index,'LTC'] = np.mean(data_cur_min[3,:4])

# Here is your main strategy function
# Note:
# 1. DO NOT modify the function parameters (time, data, etc.)
# 2. The strategy function AWAYS returns two things - position and memory:
# 2.1 position is a np.array (length 4) indicating your desired position of four crypto currencies next minute
# 2.2 memory is a class containing the information you want to save currently for future use



def handle_bar(counter,  # a counter for number of minute bars that have already been tested
               time,  # current time in string format such as "2018-07-30 00:30:00"
               data,  # data for current minute bar (in format 2)
               init_cash,  # your initial cash, a constant
               transaction,  # transaction ratio, a constant
               cash_balance,  # your cash balance at current minute
               crypto_balance,  # your crpyto currency balance at current minute
               total_balance,  # your total balance at current minute
               position_current,  # your position for 4 crypto currencies at this minute
               memory  # a class, containing the information you saved so far
               ):
    # Here you should explain the idea of your strategy briefly in the form of Python comment.
    # You can also attach facility files such as text & image & table in your team folder to illustrate your idea

    # The idea of my strategy:
    # Use Statistical Arbitage MBCHod

    
    #初始化
    if counter == 0:
        #原有仓位
        memory.position = list(position_current)
        #应有的仓位变化[BCH,BTC,ETH,LTC]
        memory.position_change = [0,0,0,0]
        
        #补仓次数初始化
        memory.HIGH_count_0,memory.HIGH_count_1 = 0,0
        memory.LOW_count_0,memory.LOW_count_1 = 0,0
        #0:非协整 1：协整套利
        memory.stage_0,memory.stage_1 = 0,0
        #记录更新参数时间
        memory.count_0,memory.count_1 = 0,0
        #记录突破止损线次数，不足次数视为假突破
        memory.count0_0,memory.count0_1 = 0,0
        #套利中的仓位
        memory.position_now_0=[0,0]
        memory.position_now_1=[0,0]
        
        memory.price_list_0 = price_list.loc[:,['BCH', 'BTC']]
        memory.price_list_1 = price_list.loc[:,['LTC', 'BTC']]
        
        memory.sp_list_0 = []
        memory.sp_list_1 = []
        #平仓线
        memory.AVERAGE_0,memory.AVERAGE_1 = 0,0
        #建仓线
        memory.HIGH_0,memory.HIGH_1 = 0,0
        memory.LOW_0,memory.LOW_1 = 0,0
        #配对系数
        memory.proportion_0,memory.proportion_1 = 0,0
        
        memory.position_sets_0 = DataFrame(
                columns = ['BTC_position',
                           'BCH_position',
                           'HIGH_stop',
                           'LOW_stop',
                           'proportion',
                           'AVERAGE',
                           'count',
                           'pvalue'])
        memory.position_sets_1 = DataFrame(
                columns = ['BTC_position',
                           'LTC_position',
                           'HIGH_stop',
                           'LOW_stop',
                           'proportion',
                           'AVERAGE',
                           'count',
                           'pvalue'])
        
    averageBCH_price = np.mean(data[assert_BCH,:4])
    averageBTC_price = np.mean(data[assert_BTC,:4])
    #averageETH_price = np.mean(data[assert_ETH,:4])
    averageLTC_price = np.mean(data[assert_LTC,:4])
    
    position = position_current
    
    #实际仓位变化
    actual_change = [position[assert_BCH]-memory.position[assert_BCH],
                     position[assert_BTC]-memory.position[assert_BTC],
                     position[assert_ETH]-memory.position[assert_ETH],
                     position[assert_LTC]-memory.position[assert_LTC]]
    #剩余未完成仓位变化
    memory.position_change = [memory.position_change[assert_BCH]-actual_change[assert_BCH],
                              memory.position_change[assert_BTC]-actual_change[assert_BTC],
                              memory.position_change[assert_ETH]-actual_change[assert_ETH],
                              memory.position_change[assert_LTC]-actual_change[assert_LTC]]
    
    #记录此时仓位，用于下次交易调用
    memory.position = list(position_current)
    
    #参数更新
    memory.price_list_0 = memory.price_list_0.append({'BCH': averageBCH_price,'BTC': averageBTC_price}, ignore_index=True)
    memory.price_list_0 = memory.price_list_0.iloc[-720:,:]
    memory.price_list_1 = memory.price_list_1.append({'LTC': averageLTC_price,'BTC': averageBTC_price}, ignore_index=True)
    memory.price_list_1 = memory.price_list_1.iloc[-720:,:]
    
    sp_0 = averageBTC_price-memory.proportion_0*averageBCH_price
    memory.sp_list_0.append(sp_0)
    memory.sp_list_0 = memory.sp_list_0[-50:]  
    
    sp_1 = averageBTC_price-memory.proportion_1*averageLTC_price
    memory.sp_list_1.append(sp_1)
    memory.sp_list_1 = memory.sp_list_1[-50:]
    
    flag = 0
    for i in memory.position_change:
        if abs(i)>0.01:
            flag = 1
    if flag:
        #完成未完成交易
        position[assert_BCH] += memory.position_change[assert_BCH]
        position[assert_BTC] += memory.position_change[assert_BTC]
        position[assert_ETH] += memory.position_change[assert_ETH]
        position[assert_LTC] += memory.position_change[assert_LTC]

    else:
        #交易对0号，BCH和BTC套利
        pvalue_0 = find_cointegrated_pairs(memory.price_list_0)
        #定义pvalue<0.45为存在协整关系，720分钟（半天）更新一次参数
        if pvalue_0  <= 0.5 and (memory.count_0 >= 720 or memory.count_0 == 0) :
            #if memory.count_0 >= 720:
            #    print(time,'更新参数')
            #else:
            #   print(time,'进入协整关系，开始套利')
            memory.sp_list_0 = []
            #补仓次数初始化
            memory.HIGH_count_0 = 0
            memory.LOW_count_0 = 0
            #存储旧仓位与旧参数
            update_0(memory,time,pvalue_0)
            
            #标记进入协整状态
            memory.stage_0 = 1
            memory.count0_0 = 0
            
            x = memory.price_list_0['BCH']
            y = memory.price_list_0['BTC']
            X = sm.add_constant(x)
            result = (sm.OLS(y.astype(float),X.astype(float))).fit()
            memory.proportion_0 = result.params[1]
            memory.AVERAGE_0 = result.params[0]

            #建仓线:加上10，确保价差的盈利能够覆盖买卖手续费
            memory.HIGH_0 =  memory.AVERAGE_0 + 10
            memory.LOW_0  =  memory.AVERAGE_0 - 10
            
            #止损线
            memory.HIGH_stop_0 =  memory.AVERAGE_0 + 120
            memory.LOW_stop_0 =  memory.AVERAGE_0 - 120
            
            sp_0 = averageBTC_price-memory.proportion_0*averageBCH_price
            arbitrage_0(total_balance,cash_balance,sp_0,position,memory,time)
            stop_0(position,memory,averageBTC_price,averageBCH_price,time)
            
            #套利持续时间更新
            memory.count_0 = 1
            
        elif pvalue_0  <= 0.5 and (memory.count_0 < 720 and memory.count_0 > 0) :
            #套利持续时间更新
            memory.count_0 += 1
            arbitrage_0(total_balance,cash_balance,sp_0,position,memory,time)
            stop_0(position,memory,averageBTC_price,averageBCH_price,time)
            
        
        #定义pvalue>0.48失去协整关系，记录此仓位组数据，仅进行止盈止损操作
        elif pvalue_0  > 0.52:
            if memory.stage_0 == 1:
                #print(time,'BTC-BCH失去协整关系')
                memory.stage_0 = 0
                #存储旧仓位与旧参数
                update_0(memory,time,pvalue_0 )
                memory.count_0 = 0
                
            stop_0(position,memory,averageBTC_price,averageBCH_price,time)
  
        #pvalue在0.45和0.48之间，暂时维持参数，但不套利，仅进行止盈止损操作
        else:
            stop_0(position,memory,averageBTC_price,averageBCH_price,time)
            if memory.stage_0 == 1:
                memory.count_0 += 1
               
        #交易对1号,ltc与btc       
        pvalue_1 = find_cointegrated_pairs(memory.price_list_1)
        #定义pvalue<0.1为存在协整关系，720分钟（半天）更新一次参数
        if pvalue_1 <= 0.45 and (memory.count_1 >= 720 or memory.count_1 == 0) :
            memory.sp_list_1 = []
            #补仓次数初始化
            memory.HIGH_count_1 = 0
            memory.LOW_count_1 = 0
            #存储旧仓位与旧参数
            update_1(memory,time,pvalue_1)

            #标记进入协整状态
            memory.stage_1 = 1
            memory.count0_1 = 0
            
            x = memory.price_list_1['LTC']
            y = memory.price_list_1['BTC']
            X = sm.add_constant(x)
            result = (sm.OLS(y.astype(float),X.astype(float))).fit()
            memory.proportion_1 = result.params[1]
            memory.AVERAGE_1 = result.params[0]
 
            #建仓线:加上0.08，确保价差的盈利能够覆盖买卖手续费
            memory.HIGH_1 =  memory.AVERAGE_1 + 10
            memory.LOW_1  =  memory.AVERAGE_1 - 10
            
            #止损线
            memory.HIGH_stop_1 =  memory.AVERAGE_1 + 120
            memory.LOW_stop_1  =  memory.AVERAGE_1 - 120
            
            sp_1 = averageBTC_price-memory.proportion_1*averageLTC_price
            arbitrage_1(total_balance,cash_balance,sp_1,position,memory,time)
            stop_1(position,memory,averageBTC_price,averageLTC_price,time)
            
            #套利持续时间更新
            memory.count_1 = 1
            
        elif pvalue_1 <= 0.45 and (memory.count_1 < 720 and memory.count_1 > 0) :
            #套利持续时间更新
            memory.count_1 += 1
            arbitrage_1(total_balance,cash_balance,sp_1,position,memory,time)
            stop_1(position,memory,averageBTC_price,averageLTC_price,time)
            
        
        #定义pvalue>0.1失去协整关系，记录此仓位组数据，仅进行止盈止损操作
        elif pvalue_1 > 0.48:
            if memory.stage_1 == 1:
                #print(time,'失去协整关系')
                memory.stage_1 = 0
                #存储旧仓位与旧参数
                update_1(memory,time,pvalue_1)
                memory.count_1 = 0
                
            stop_1(position,memory,averageBTC_price,averageLTC_price,time)
  
        #pvalue在0.15和0.17之间，暂时维持参数，但不套利，仅进行止盈止损操作
        else:
            stop_1(position,memory,averageBTC_price,averageLTC_price,time)
            if memory.stage_1 == 1:
                memory.count_1 += 1
    return position, memory

#套利方法
def arbitrage_0(total_balance,cash_balance,sp,position,memory,time):
    #保持为总仓位的80%，且最多补仓4次
    if cash_balance/total_balance>=0.2 and memory.proportion_0 > 3 and memory.proportion_0 < 11.5:
        if sp > memory.HIGH_0 and sp < memory.HIGH_stop_0 and (not delay(memory.sp_list_0,n=15)) and delay(memory.sp_list_0,n=15) != 2:
            
            if memory.HIGH_count_0 == 0:
                memory.HIGH_stop_0 = sp + 100
                memory.position_change[assert_BCH] += exchange[0]*memory.proportion_0
                memory.position_change[assert_BTC] -= exchange[0]
                
                position[assert_BCH] += exchange[0]*memory.proportion_0
                position[assert_BTC] -= exchange[0]
                
                memory.position_now_0 = [memory.position_now_0[0]+exchange[0]*memory.proportion_0,
                                         memory.position_now_0[1]-exchange[0]]
            else:
                memory.position_change[assert_BCH] += exchange[0]*0.5*memory.proportion_0
                memory.position_change[assert_BTC] -= exchange[0]*0.5
                
                position[assert_BCH] += exchange[0]*0.5*memory.proportion_0
                position[assert_BTC] -= exchange[0]*0.5
                
                memory.position_now_0 = [memory.position_now_0[0]+exchange[0]*0.5*memory.proportion_0,
                                         memory.position_now_0[1]-exchange[0]*0.5]
                
            memory.HIGH_count_0 += 1
            if memory.HIGH_count_0 >= 5:
                memory.count_0 = 0
            
        elif sp < memory.LOW_0 and sp > memory.LOW_stop_0 and delay(memory.sp_list_0,n=15) and delay(memory.sp_list_0,n=15) != 2:
            
            if memory.LOW_count_0 == 0:
                memory.LOW_stop_0 = sp - 100
                memory.position_change[assert_BCH] -= exchange[0]*memory.proportion_0
                memory.position_change[assert_BTC] += exchange[0]
            
                position[assert_BCH] -= exchange[0]*memory.proportion_0
                position[assert_BTC] += exchange[0]
                
                memory.position_now_0 = [memory.position_now_0[0]-exchange[0]*memory.proportion_0,
                                         memory.position_now_0[1]+exchange[0]]
                
            else:
                memory.position_change[assert_BCH] -= exchange[0]*0.5*memory.proportion_0
                memory.position_change[assert_BTC] += exchange[0]*0.5
            
                position[assert_BCH] -= exchange[0]*0.5*memory.proportion_0
                position[assert_BTC] += exchange[0]*0.5
                
                memory.position_now_0 = [memory.position_now_0[0]-exchange[0]*0.5*memory.proportion_0,
                                         memory.position_now_0[1]+exchange[0]*0.5]
            memory.LOW_count_0 += 1      
            if memory.LOW_count_0 >= 5:
                memory.count_0 = 0
            
    flag = 1 if memory.HIGH_count_0 > 0 else -1       
    #价差回归时平仓止盈，突破止损线时止损，补仓次数归零
    if (sp > memory.HIGH_stop_0 and memory.HIGH_count_0>0) or (sp < memory.LOW_stop_0 and memory.LOW_count_0>0):
        memory.count0_0 += 1
        if memory.count0_0 == 20:

            memory.position_change[assert_BCH] -= memory.position_now_0[0]
            memory.position_change[assert_BTC] -= memory.position_now_0[1]
            
            position[assert_BCH] -= memory.position_now_0[0]
            position[assert_BTC] -= memory.position_now_0[1]
            
            memory.HIGH_count_0,memory.LOW_count_0 = 0,0
            memory.count0_0 = 0
            memory.position_now_0 = [0,0]
            print(time,'BTC_BCH止损平仓')
    
    elif flag*(sp - memory.AVERAGE_0) < 0.1 and (memory.HIGH_count_0>0 or memory.LOW_count_0>0):
        memory.position_change[assert_BCH] -= memory.position_now_0[0]
        memory.position_change[assert_BTC] -= memory.position_now_0[1]
        
        position[assert_BCH] -= memory.position_now_0[0]
        position[assert_BTC] -= memory.position_now_0[1]
        
        memory.HIGH_count_0,memory.LOW_count_0 = 0,0
        memory.count0_0 = 0
        memory.position_now_0 = [0,0]
        print(time,'BTC_BCH止盈平仓')

def arbitrage_1(total_balance,cash_balance,sp,position,memory,time):
    #保持为总仓位的70%，且最多补仓4次
    if cash_balance/total_balance>=0.2 and memory.proportion_1 > 0 and memory.proportion_1 < 95:
        if sp > memory.HIGH_1 and sp < memory.HIGH_stop_1 and (not delay(memory.sp_list_1,n=10)) and delay(memory.sp_list_1,n=10) != 2:
            
            if memory.HIGH_count_1 == 0:
                memory.HIGH_stop_1 = sp + 100
                memory.position_change[assert_LTC] += exchange[0]*memory.proportion_1
                memory.position_change[assert_BTC] -= exchange[0]
                
                position[assert_LTC] += exchange[0]*memory.proportion_1
                position[assert_BTC] -= exchange[0]
                
                memory.position_now_1 = [memory.position_now_1[0]+exchange[0]*memory.proportion_1,
                                         memory.position_now_1[1]-exchange[0]]
            else:
                memory.position_change[assert_LTC] += exchange[0]*0.5*memory.proportion_1
                memory.position_change[assert_BTC] -= exchange[0]*0.5
                
                position[assert_LTC] += exchange[0]*0.5*memory.proportion_1
                position[assert_BTC] -= exchange[0]*0.5
                
                memory.position_now_1 = [memory.position_now_1[0]+exchange[0]*0.5*memory.proportion_1,
                                         memory.position_now_1[1]-exchange[0]*0.5]
                
            memory.HIGH_count_1 += 1
            if memory.HIGH_count_1 >= 5:
                memory.count_1 = 0
            
        elif sp < memory.LOW_1 and sp > memory.LOW_stop_1 and delay(memory.sp_list_1,n=10) and delay(memory.sp_list_1,n=10) != 2:
            
            if memory.LOW_count_1 == 0:
                memory.LOW_stop_1 = sp - 100
                memory.position_change[assert_LTC] -= exchange[0]*memory.proportion_1
                memory.position_change[assert_BTC] += exchange[0]
            
                position[assert_LTC] -= exchange[0]*memory.proportion_1
                position[assert_BTC] += exchange[0]
                
                memory.position_now_1 = [memory.position_now_1[0]-exchange[0]*memory.proportion_1,
                                         memory.position_now_1[1]+exchange[0]]
                
            else:
                memory.position_change[assert_LTC] -= exchange[0]*0.5*memory.proportion_1
                memory.position_change[assert_BTC] += exchange[0]*0.5
            
                position[assert_LTC] -= exchange[0]*0.5*memory.proportion_1
                position[assert_BTC] += exchange[0]*0.5
                
                memory.position_now_1 = [memory.position_now_1[0]-exchange[0]*0.5*memory.proportion_1,
                                         memory.position_now_1[1]+exchange[0]*0.5]
            memory.LOW_count_1 += 1      
            if memory.LOW_count_1 >= 5:
                memory.count_1 = 0
            
    flag = 1 if memory.HIGH_count_1 > 0 else -1       
    #价差回归时平仓止盈，突破止损线时止损，补仓次数归零
    if (sp > memory.HIGH_stop_1 and memory.HIGH_count_1>0) or (sp < memory.LOW_stop_1 and memory.LOW_count_1>0):
        memory.count0_1 += 1
        if memory.count0_1 == 20:

            memory.position_change[assert_LTC] -= memory.position_now_1[0]
            memory.position_change[assert_BTC] -= memory.position_now_1[1]
            
            position[assert_LTC] -= memory.position_now_1[0]
            position[assert_BTC] -= memory.position_now_1[1]
            
            memory.HIGH_count_1,memory.LOW_count_1 = 0,0
            memory.count0_1 = 0
            memory.position_now_1 = [0,0]
            print(time,'BTC_LTC止损平仓')
    
    elif flag*(sp - memory.AVERAGE_1) < 0.1 and (memory.HIGH_count_1>0 or memory.LOW_count_1>0):
        memory.position_change[assert_LTC] -= memory.position_now_1[0]
        memory.position_change[assert_BTC] -= memory.position_now_1[1]
        
        position[assert_LTC] -= memory.position_now_1[0]
        position[assert_BTC] -= memory.position_now_1[1]
        
        memory.HIGH_count_1,memory.LOW_count_1 = 0,0
        memory.count0_1 = 0
        memory.position_now_1 = [0,0]
        print(time,'BTC_LTC止盈平仓')

#计算pvalue
def find_cointegrated_pairs(df):
    # 获取相应的两只币种的价格
    stock1 = df.iloc[:,0].astype(float)
    stock2 = df.iloc[:,1].astype(float)
    # 分析它们的协整关系
    result = sm.tsa.stattools.coint(stock1, stock2)
    # 取出并记录p值
    pvalue = result[1]
    # 返回结果
    return pvalue

#更新仓位组
def update_0(memory,time,pvalue): 
    #若此刻仓位不为0则更新
    if abs(memory.position_now_0[0]) > 0.1:  
        #由于参数已经更新，旧参数建的仓风险增加，因此加上10使止损更加严格
        memory.position_sets_0 = memory.position_sets_0.append({'BTC_position': memory.position_now_0[1],
                                                            'BCH_position': memory.position_now_0[0],
                                                            'HIGH_stop': memory.HIGH_stop_0-15,
                                                            'LOW_stop': memory.LOW_stop_0+15,
                                                            'proportion': memory.proportion_0,
                                                            'AVERAGE': memory.AVERAGE_0,
                                                            'count': memory.count0_0,
                                                            'pvalue': pvalue },ignore_index=True)
    
        print(time,'更新BTC_BCH仓位组','\n',memory.position_sets_0.iloc[:,[0,1,2,3,4]])
    memory.position_now_0 = [0,0]

def update_1(memory,time,pvalue): 
    #若此刻仓位不为0则更新
    if abs(memory.position_now_1[0]) > 0.1:  
        #由于参数已经更新，旧参数建的仓风险增加，因此加上15使止损更加严格
        memory.position_sets_1 = memory.position_sets_1.append({'BTC_position': memory.position_now_1[1],
                                                            'LTC_position': memory.position_now_1[0],
                                                            'HIGH_stop': memory.HIGH_stop_1-15,
                                                            'LOW_stop': memory.LOW_stop_1+15,
                                                            'proportion': memory.proportion_1,
                                                            'AVERAGE': memory.AVERAGE_1,
                                                            'count': memory.count0_1,
                                                            'pvalue': pvalue},ignore_index=True)
    
        print(time,'更新BTC_LTC仓位组','\n',memory.position_sets_1.iloc[:,[0,1,2,3,4]])
    memory.position_now_1 = [0,0]
        
#对各仓位组处理，价差回归时平仓，突破止损线时止损  
def stop_0(position,memory,averageBTC_price,averageBCH_price,time):
    for indexs in memory.position_sets_0.index:
        sp = averageBTC_price-memory.position_sets_0.loc[indexs,'proportion']*averageBCH_price

        #由于旧仓位风险过高，放宽平仓条件为1提前平仓
        flag = 1 if memory.position_sets_0.loc[indexs,'BTC_position']<0 else -1 
        if sp > memory.position_sets_0.loc[indexs,'HIGH_stop'] or sp < memory.position_sets_0.loc[indexs,'LOW_stop']:
            memory.position_sets_0.loc[indexs,'count'] += 1
            if memory.position_sets_0.loc[indexs,'count'] == 60:
                position[assert_BTC] -= memory.position_sets_0.loc[indexs,'BTC_position']
                position[assert_BCH] -= memory.position_sets_0.loc[indexs,'BCH_position']
                memory.position_change[assert_BTC] -= memory.position_sets_0.loc[indexs,'BTC_position']
                memory.position_change[assert_BCH] -= memory.position_sets_0.loc[indexs,'BCH_position']
                #print(time,'BTC_BCH现有仓位组','\n',memory.position_sets_0)
                print(time,'BTC_BCH仓位组：',indexs,'止损平仓')
                memory.position_sets_0.drop(index = indexs, inplace = True)
                break
                    
        elif flag*(sp - memory.position_sets_0.loc[indexs,'AVERAGE']) < 1:
            position[assert_BTC] -= memory.position_sets_0.loc[indexs,'BTC_position']
            position[assert_BCH] -= memory.position_sets_0.loc[indexs,'BCH_position']
            memory.position_change[assert_BTC] -= memory.position_sets_0.loc[indexs,'BTC_position']
            memory.position_change[assert_BCH] -= memory.position_sets_0.loc[indexs,'BCH_position']
            #print(time,'BTC_BCH现有仓位组','\n',memory.position_sets_0)
            print(time,'BTC_BCH仓位组：',indexs,'止盈平仓')  
            memory.position_sets_0.drop(index = indexs, inplace = True)  
            break
        
def stop_1(position,memory,averageBTC_price,averageLTC_price,time):
    for indexs in memory.position_sets_1.index:
        sp = averageBTC_price-memory.position_sets_1.loc[indexs,'proportion']*averageLTC_price
        #由于旧仓位风险过高，放宽平仓条件为1提前平仓
        flag = 1 if memory.position_sets_1.loc[indexs,'BTC_position']<0 else -1 
        if sp > memory.position_sets_1.loc[indexs,'HIGH_stop'] or sp < memory.position_sets_1.loc[indexs,'LOW_stop']:
            memory.position_sets_1.loc[indexs,'count'] += 1
            if memory.position_sets_1.loc[indexs,'count'] == 60:
                position[assert_BTC] -= memory.position_sets_1.loc[indexs,'BTC_position']
                position[assert_LTC] -= memory.position_sets_1.loc[indexs,'LTC_position']
                memory.position_change[assert_BTC] -= memory.position_sets_1.loc[indexs,'BTC_position']
                memory.position_change[assert_LTC] -= memory.position_sets_1.loc[indexs,'LTC_position']
                #print(time,'BTC_LTC现有仓位组','\n',memory.position_sets_1)
                print(time,'BTC_LTC仓位组：',indexs,'止损平仓')
                memory.position_sets_1.drop(index = indexs, inplace = True)
                break
                    
        elif flag*(sp - memory.position_sets_1.loc[indexs,'AVERAGE']) < 1:
            position[assert_BTC] -= memory.position_sets_1.loc[indexs,'BTC_position'] 
            position[assert_LTC] -= memory.position_sets_1.loc[indexs,'LTC_position']
            memory.position_change[assert_BTC] -= memory.position_sets_1.loc[indexs,'BTC_position']
            memory.position_change[assert_LTC] -= memory.position_sets_1.loc[indexs,'LTC_position']
            #print(time,'BTC_LTC现有仓位组','\n',memory.position_sets_1)
            print(time,'BTC_LTC仓位组：',indexs,'止盈平仓')    
            memory.position_sets_1.drop(index = indexs, inplace = True)  
            break
#延迟开仓策略,仅在价差反向突破时开仓，避免价差的单边行情
#取最近的n个价差，其趋势用斜率表示。            
def delay(sp_list,n):
    try:
        x = list(range(n))
        y = sp_list[-n:]
        X = sm.add_constant(x)
        result = (sm.OLS(y,X)).fit()
        k = result.params[1]
        return True if k>0 else False
    
    except BaseException:
        #使用2代表价差列表暂时不够判断趋势
        return 2

          
