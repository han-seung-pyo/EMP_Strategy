'''
empm5lev.py
내용 : 레버리지(122630) 비중 CAP 추가 

'''
import numpy as np
import pandas as pd

#DATA
price=pd.read_excel("emp_price_20180528.xlsx",index_col=0)
etf=pd.read_excel("etf.xlsx",index_col=0)

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
alletf['122630']=price['122630']
alletf['069500']=price['069500']
#alletf.to_excel('all_etf.xlsx') #엑셀파일로 저장

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
# rebal_num[0] : each_rebal - 모멘텀 계산하는 1년치 날짜 갯수
# rebal_num[1] : monthly_data - 1달 날짜 갯수 

#etf 포트폴리오 DataFrfame call
#i=portfolio number, num=each_rebal, j=monthly_data
def etf_call(i,num,j):
    a=5*i
    b=5*(i+1)
    temp=0
    for k in range(num):
        temp+=month_date[k]
    c=temp
    d=temp+j
    return alletf.iloc[c:d,a:b]

#Momentum 계산
def momentum(price):
    momentum=(((price.iloc[len(price)-1]/price)-1)*100).mean()
    return momentum

#Momentum Filter 적용 후 Portfolio
def momentum_filter(momentum):
    pf=[] #porfolio 
    l=list(dict(momentum).keys())
    i=0
    for i in range(len(momentum)):
        if momentum[i]>1:
            pf.append(l[i])
    return pf

#momentum>1인 etf들로 포트폴리오 구성
def port(pf,called):
    port=pd.DataFrame()
    for i in range(len(pf)):
        port=pd.concat([port,pd.DataFrame(called[pf[i]].values)],1)
    port.index=called.index
    port.columns=pf
    return port

#Correlation 계산
def etf_corr(d):
    df=[] #5개 종목 equaly weighted portfolio
    for i in range(len(d.index)):
        df.append((d.iloc[i,0:5].sum())/5)
    newdf=pd.DataFrame(df)
    newdf.index=d.index
    finaldf=pd.concat([newdf,d],1)
    c=finaldf.corrwith(finaldf[0])
    return c[1:6]

#std 계산
def etf_std(d):
    return d.std()

#투자비중 계산
def etf_weight(c,s,port,cap):
    w_kodex=0
    names=list(port.columns)
    n=len(port.columns)
    w_kodex=(5-n)/5
    w=[]
    for i in range(n):
        w.append((1-c[names[i]])/(s[names[i]]))
    w=pd.DataFrame(w)
    weight=(w/(w.sum()))*(n/5)
    if w_kodex>cap:
        new_weight=w_kodex-cap
        weight=weight+(new_weight/n)
        w_kodex=cap
    final_w=list(weight[0])
    final_w.append(w_kodex)
    return final_w

#샤프비율 구하기
def sharpe(rs,mkt):
    mkt_m=float(mkt.pct_change().cumsum().tail(1).iloc[0])
    sr=((rs[1].values-mkt_m)/rs[0].values)
    return sr

#수익률 관찰 포트에 Kodex200 데이터 추가
def market(num,j):
    temp=0
    for k in range(num):
        temp+=month_date[k]
    c=temp
    d=temp+j
    return alletf['122630'].iloc[c:d]

#수익률 관찰 포트에 Kodex200 데이터 추가
def market_forsharp(num,j):
    temp=0
    for k in range(num):
        temp+=month_date[k]
    c=temp
    d=temp+j
    return alletf['069500'].iloc[c:d]

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

#MAIN
k=0
sr=[]
sec=[]
dd=pd.DataFrame()
dd_name_f=pd.DataFrame()
caps=[0.05,0.1,0.15,0.2,0.25,0.3]
cap=0
count=0

for i in range(36):
    for cap in caps:
        for j in range(len(tot_date)):
            etf_called=etf_call(i,j,tot_date[j])
            mom=momentum(etf_called)
            pf=momentum_filter(mom)
            if len(pf)==0:
                mk=market(12+j,month_date[12+j])
                mk=pd.DataFrame(mk)
                rs=port_ret_s([0.0,1.0],mk,mk)
                dd=pd.concat([dd,rs])
                sec=list(['122630'])
                sr.append(sharpe(rs,pd.DataFrame(market_forsharp(12+j,month_date[12+j]))))
                u=mk.index.to_datetime()
                y=u[0].year
                m=u[0].month
                ym=[y,m]
                c=str(ym[0])+'-'+str(ym[1])
                dd_name=pd.DataFrame()
                dd_name['port']=[i]
                dd_name['num']=[j]
                dd_name['cap']=[cap]
                dd_name['month']=[c]
                dd_name['security']=[sec]
                dd_name['weight']=[[0.0,1.0]]
                dd_name_f=pd.concat([dd_name_f,dd_name])
                #print(j,sec,sr[-1],1.0)
                continue
            pt=port(pf,etf_called)
            c=etf_corr(etf_called) 
            s=etf_std(etf_called)
            w=etf_weight(c,s,pt,cap)
            etf_return=etf_call(i,12+j,month_date[12+j])
            pr=port(pf,etf_return)
            mk=market(12+j,month_date[12+j])
            rs=port_ret_s(w,pr,mk)
            dd=pd.concat([dd,rs])
            sec=list(pt.columns)
            sec.append('122630')
            sr.append(sharpe(rs,pd.DataFrame(market_forsharp(12+j,month_date[12+j]))))
            u=pr.index.to_datetime()
            y=u[0].year
            m=u[0].month
            ym=[y,m]
            c=str(ym[0])+'-'+str(ym[1])
            dd_name=pd.DataFrame()
            dd_name['port']=[i]
            dd_name['num']=[j]
            dd_name['cap']=[cap]
            dd_name['month']=[c]
            dd_name['security']=[sec]
            dd_name['weight']=[w]
            dd_name_f=pd.concat([dd_name_f,dd_name])
            #print(j,sec,sharpe(rs,mk),w)

sr=pd.DataFrame(sr)
sr.index=dd.index
dd_final=pd.concat([dd,sr],axis=1)
dd_name_f.index=dd_final.index
dd_final=pd.concat([dd_name_f,dd_final],1)
dd_final.columns=['port','num','cap','month','security','weight','std','return','sr']
dd_final.index=dd_final.pop("port")

dd_final.to_excel('final_empm5lev.xlsx')