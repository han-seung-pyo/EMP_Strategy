'''
plot_test.py
수익률 기준 및 sr 기준 cumsum plot 용

'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


final_return=pd.read_excel("test2_result_20180614.xlsx")
final_sr=pd.read_excel("test2_sr_result_20180614.xlsx")
equal_price=pd.read_excel("equal_weighted_price_20180614.xlsx")
aismb=pd.read_excel("emp_fund_price_20180614.xlsx",index_col=0)
t=aismb.index.to_datetime()


equal_df=pd.DataFrame()
fund_df=pd.DataFrame()
ew=[]

for i in range(len(equal_price)):
    ew.append(float((equal_price.iloc[i,:].sum())/5))

equal_df['price']=ew
equal_df.index=equal_price.index

fund_df['return']=aismb['price']
fund_df.index=t

cp=final_return['return'].cumsum()
cs=final_sr['return'].cumsum()
cm=final_return['mk'].cumsum()
cm_equal=equal_df.pct_change().cumsum().resample('M').last()
cm_fund=fund_df.pct_change().cumsum().resample('M').last()

plt.plot(cp,color='green', label = 'return')
plt.plot(cs,color='blue', label = 'sr')
plt.plot(cm,color='red', label = 'market')
cm_equal.index=cm.index
plt.plot(cm_equal,color='orange', label = 'equal')
plt.title('Best portfolio result')
plt.legend()

plt.show()

re_cp=pd.DataFrame()
re_cp=final_return['return'].iloc[7:].cumsum()
plt.plot(re_cp,color='green', label = 'return')
cm_fund.index=re_cp.index
plt.plot(cm_fund,color='red', label = 'fund')
plt.title('Best portfolio vs Port')
plt.legend()

plt.show()
