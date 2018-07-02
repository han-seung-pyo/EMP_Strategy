'''
test2.py
수익률 관찰 용

'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

price=pd.read_excel("emp_price_20180614.xlsx",index_col=0)
etf=pd.read_excel("etf.xlsx",index_col=0)
price_kospi=pd.read_excel("kospi_price_20180614.xlsx",index_col=0)

final_m1=pd.read_excel("final_empm1_20180614.xlsx")
final_m2=pd.read_excel("final_empm2_20180614.xlsx")
final_m3inv=pd.read_excel("final_empm3inv_20180614.xlsx")
final_m3lev=pd.read_excel("final_empm3lev_20180614.xlsx")
final_m4inv=pd.read_excel("final_empm4inv_20180614.xlsx")
final_m4lev=pd.read_excel("final_empm4lev_20180614.xlsx")
final_m5inv=pd.read_excel("final_empm5inv_20180614.xlsx")
final_m5lev=pd.read_excel("final_empm5lev_20180614.xlsx")

finals=[final_m1,final_m2,final_m3inv,final_m3lev,final_m4inv,final_m4lev,final_m5inv,final_m5lev]

#전체 etf 포트폴리오 구성
def all_etf_port(etf):
    result = pd.DataFrame()
    etf_col = etf.columns
    for i in range(36):
        code = (etf[etf_col[i]])
        for i in code:
            result = pd.concat([result, price[str(i)]], axis=1)
    return result

alletf=all_etf_port(etf) #맨처음에 한번만 만들면 됨
alletf['069500']=price['069500']
alletf['kospi']=price_kospi['kospi']

#Datetime이용해서 월별 데이터 갯수 및 rebalancing마다 데이터 갯수 저장
def freq(price):
    t=price.index.to_datetime()
    monthly_data=[]
    each_rebal=[]

    for i in range(len(price)-1):
        if t[i].month!=t[i+1].month:
            a=t[i].year
            b=t[i].month
            p=[a,b]
            c=str(p[0])+'-'+str(p[1])
            monthly_data.append(len(price[c]))
    last=len(price)-1
    a=t[last].year
    b=t[last].month
    p=[a,b]
    c=str(p[0])+'-'+str(p[1])
    monthly_data.append(len(price[c]))

    for j in range(len(monthly_data)-12):
        temp=0
        for k in range(12):
            temp+=monthly_data[j+k]
        each_rebal.append(temp)

    return each_rebal,monthly_data

rebal_num=freq(price) #한번만 호출하면 됨
tot_date=rebal_num[0]
month_date=rebal_num[1]

rebal=len(month_date)-12 #global 변수, rebalancing 횟수 저장

#index를 모두 month로 바꾸고 datetime으로 바꿔줌
for final in finals:
    final.index=final.pop("month")
    final.index=final.index.to_datetime()

#각 모델의, 동일 월 내에서 best 수익률의 port 정보를 뽑아줌
def model_best(i):#i:해당하는 월 순번(num)(ex.2016-05, 2016-06 등)
    t=finals[0].index[i]
    port_port=[]
    port_num=[]
    port_w=[]
    port_sec=[]
    port_ret=[]
    tot_port=pd.DataFrame()    
    for final in finals:
        c=str(t.year)+'-'+str(t.month)
        for j in range(len(final[c])):
            if final[c]['return'].iloc[j]==final[c]['return'].max():
                port_port.append(final[c]['port'].iloc[j])
                port_num.append(final[c]['num'].iloc[j])
                port_w.append(final[c]['weight'].iloc[j])
                port_sec.append(final[c]['security'].iloc[j])
                port_ret.append(final[c]['return'].iloc[j])
                break
    tt=[]
    for i in range(8):
        tt.append(t)
    tot_port['month']=tt
    tot_port['port']=port_port
    tot_port['num']=port_num
    tot_port['weight']=rep_list_w(port_w)
    tot_port['security']=rep_list_s(port_sec)
    tot_port['return']=port_ret
    tot_port.index=tt

    return tot_port
    
#etf_call 함수
def etf_call(i,num,j):
    a=5*i
    b=5*(i+1)
    temp=0
    for k in range(num):
        temp+=month_date[k]
    c=temp
    d=temp+j
    return alletf.iloc[c:d,a:b]

#pf 리스트에 따라 뽑힌 종목들로 포트폴리오 구성
def port(pf,called):
    port=pd.DataFrame()
    for i in range(len(pf)):
        port=pd.concat([port,pd.DataFrame(called[pf[i]].values)],1)
    port.index=called.index
    port.columns=pf
    return port

#final 파일로 부터 weight부분 반환
def rep_list_w(strings):
    n=len(strings)
    final=[]
    for i in range(n):
        s = strings[i]
        l = s.replace("[","").replace("]","").replace(" ","").split(",")
        final_list=[]
        for j in range(len(l)):
            final_list.append(float(l[j]))
        final.append(final_list)
    return final

#final 파일로 종목명 부분 반환
def rep_list_s(strings):
    n=len(strings)
    final=[]
    for i in range(n):
        s = strings[i]
        l = s.replace("[","").replace("]","").replace(" ","").replace("\'","").split(",")
        final_list=[]
        for j in range(len(l)):
            final_list.append(l[j])
        final.append(final_list)
    return final

#각 모델별로 뽑힌 베스트 중에 가장 높은 수익률을 또 뽑아서 전체 모델 중 베스트 port를 best_port로 반환함 - 전체 월별 모두
def best(): #25숫자 round(rebalancing 횟수)로 일반화 시키기
    final=pd.DataFrame()
    port_port=[]
    port_month=[]
    port_num=[]
    port_model=[]
    port_w=[]
    port_sec=[]
    port_ret=[]
    best_port=pd.DataFrame()
    for i in range(rebal):
        final=model_best(i)
        for j in range(8):
            if final['return'].iloc[j]==final['return'].max():
                port_port.append(final['port'].iloc[j])
                port_month.append(final['month'].iloc[j])
                port_num.append(final['num'].iloc[j])
                port_model.append(j)
                port_w.append(final['weight'].iloc[j])
                port_sec.append(final['security'].iloc[j])
                port_ret.append(final['return'].iloc[j])
                break
    best_port['port']=port_port
    best_port['month']=port_month
    best_port['num']=port_num
    best_port['model']=port_model
    best_port['weight']=port_w
    best_port['security']=port_sec
    best_port['return']=port_ret
    best_port.index=best_port.pop("month")

    return best_port

#수익률 관찰 포트에 Kodex200 데이터 추가
def market(num,j):
    temp=0
    for k in range(num):
        temp+=month_date[k]
    c=temp
    d=temp+j
    return alletf['069500'].iloc[c:d]

def mk_kospi(num,j):
    temp=0
    for k in range(num):
        temp+=month_date[k]
    c=temp
    d=temp+j
    return alletf['kospi'].iloc[c:d]

#포트폴리오 수익률, 표준편차 구하기
def port_ret_s(w,port,mkt): ##port=pt:포트폴리오 전체 가격이랑 같이(DF), pf=pf:컬럼 리스트만
    ret_port_m=pd.Series(port.pct_change().cumsum().tail(1).iloc[0,:])
    ret_port=port.pct_change()
    mkt_m=float(mkt.pct_change().cumsum().tail(1).iloc[0])
    mkt=mkt.pct_change()
    ret_port_m=list(ret_port_m)
    ret_port_m.append(mkt_m)
    ret=[]
    for i in range(len(port.columns)+1):
        ret.append(ret_port_m[i]*w[i])
    temp=pd.DataFrame(ret)
    port_r=temp.sum()
    
    ret_p=pd.DataFrame()
    ret_p_final=[]
    
    for j in range(len(port.columns)):
        ret_p=pd.concat([ret_p,((pd.DataFrame(ret_port[port.columns[j]].values))*w[j])],1)
    mkt=mkt*w[-1]
    ret_p.index=mkt.index
    ret_p=pd.concat([ret_p,mkt],1)
    
    for k in range(len(port.index)):
        ret_p_final.append(ret_p.iloc[k,:].sum())
    ret_p_final=pd.DataFrame(ret_p_final)
    ret_std=pd.DataFrame()
    ret_std=ret_p_final.std()
    ret_final=pd.concat([ret_std,port_r],1)
    
    return ret_final

i,j=0,0

dd=pd.DataFrame()
dd_date=[]
dd_mk=[]
best_port=pd.DataFrame()

best_port=best()
best_port.to_excel('all_best_port_return_20180614.xlsx')

for k in range(rebal-1):
    i=best_port['port'][k]
    j=best_port['num'][k]
    pf=best_port['security'][k][0:-1]

    if len(pf)==0:
        mk=market(13+j,month_date[13+j])
        mk=pd.DataFrame(mk)
        rs=port_ret_s([0.0,1.0],mk,mk)
        dd_date.append(mk.index[-1])
        mkk=mk_kospi(13+j,month_date[13+j])
        mkm=float(mkk.pct_change().cumsum().tail(1).iloc[0])
        dd_mk.append(mkm)
        print(mk.index[-1],float(rs[1]),mkm)
        dd=pd.concat([dd,rs])
        continue
    w=best_port['weight'][k]    
    etf_return=etf_call(i,13+j,month_date[13+j])
    pr=port(pf,etf_return)
    mk=market(13+j,month_date[13+j])
    rs=port_ret_s(w,pr,mk)
    dd_date.append(mk.index[-1])
    mkk=mk_kospi(13+j,month_date[13+j])
    mkm=float(mkk.pct_change().cumsum().tail(1).iloc[0])
    dd_mk.append(mkm)
    print(mk.index[-1],float(rs[1]),mkm)
    dd=pd.concat([dd,rs])

dd.index=dd_date
dd.columns=['std','return']
dd['mk']=dd_mk

dd.to_excel('test2_result_20180614.xlsx')

cp=dd['return'].cumsum()
cm=dd['mk'].cumsum()
plt.plot(cp,color='green', label = 'port')
plt.plot(cm,color='red', label = 'market')
plt.title('Best port Result_Return')
plt.legend()

plt.show()


############################################################################
def ranking(i):
    t=finals[0].index[i]
    port_port=[]
    port_num=[]
    port_w=[]
    port_sec=[]
    port_ret=[]
    tot_port = pd.DataFrame()
    all_pd = pd.DataFrame()
    for final in finals:
        c=str(t.year)+'-'+str(t.month)
        for j in range(len(final[c]))::
            port_port.append(final[c]['port'].iloc[j])
            port_num.append(final[c]['num'].iloc[j])
            port_w.append(final[c]['weight'].iloc[j])
            port_sec.append(final[c]['security'].iloc[j])
            port_ret.append(final[c]['return'].iloc[j])
            
    tt=[]
    for i in range(8):
        tt.append(t)
    tot_port['month']=tt
    tot_port['port']=port_port
    tot_port['num']=port_num
    tot_port['weight']=rep_list_w(port_w)
    tot_port['security']=rep_list_s(port_sec)
    tot_port['return']=port_ret
    tot_port.index=tt

    return tot_port

aaa = ranking(1)
############################################################################