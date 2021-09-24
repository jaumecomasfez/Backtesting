import time
import csv
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader.data as wb
import numpy as np
import seaborn as sns
import csv
import datetime as dt
import yfinance as yf
import pandas_datareader as wb

## Ajustes estrategia ##

MAs = 6 # inicio media movil corta
MAl = 8 # inicio media movil larga
x = 0 # numero de ciclos
comision = 0.1 # comision por operacion

assets = ['BTC-USD']
start_time = dt.datetime(2020,9,13)
end_time = dt.datetime(2021,9,13) 
data =  yf.download(assets,start=start_time,end=end_time,interval="1h",auto_adjust=True)
f = open('BTC_EMA_cl_EMA_cl_tf1h_t1Y.csv', 'w') # asset, primer media + fuente, segunda media + fuente, fimeframe, timempo de backtest
data = data['Close']

total = pd.DataFrame()
data.index = pd.to_datetime(data.index)

# Crear y definir filas del csv #

writer = csv.writer(f)
writer.writerow(["Setting", "Total of trades","Restult in %", "Result in $", "Profit factor", "Win ratio %", "Expected value","Profit/Loss ratio", "Average Gain", "Average Loss", "Number of gains", "Number of losses", "x"])


startt = time.time() # contador para cuanto tarda en calcular cada setting

while MAl < 15: # hasta que numero es la media movil mas grande,

    signal = pd.DataFrame(index=data.index)

    signal['short'] = data.ewm(MAs).mean()
    signal['long'] = data.ewm(MAl).mean()
    signal['short'] = signal['short'].iloc[MAl:]

    signal['signals'] = np.where(signal['short'] > signal['long'], 1, 0)
    signal['positions'] = signal['signals'].diff()
    signal['a'] = 0
    
    bpa = [] # precios donde se comrpa
    spa = [] # precios donde se vende
    percentage = [] # porcentaje de ganancia o perdida de
    
    ## calcular el porcentaje de ganancia o perdida de cada tarde ##
    
    for r in range(len(signal['signals'])):
        if (signal['short'].iloc[r] > signal['long'].iloc[r]) & (signal['short'].iloc[r-1] < signal['long'].iloc[r-1]):
            bp=round(data.iloc[r],2)
            bpa.append(bp)
            
        elif (signal['short'].iloc[r] < signal['long'].iloc[r]) & (signal['short'].iloc[r-1] > signal['long'].iloc[r-1]):
            sp=round(data.iloc[r],2)
            spa.append(sp)
    
    if len(bpa) > len(spa):             
        for t in range(len(spa)):
            pc = round((spa[t]/bpa[t]-1)*100 - comision,2)
            percentage.append(pc)  
    
    if len(bpa) < len(spa):             
        for t in range(len(bpa)):
            pc = round((spa[t]/bpa[t]-1)*100 - comision,2)
            percentage.append(pc)
            
    if len(bpa) == len(spa):             
        for t in range(len(bpa)):
            pc = round((spa[t]/bpa[t]-1)*100 - comision,2)
            percentage.append(pc)   
   
    capital = int(100000)
    stocks = 3

    positions = pd.DataFrame(index=signal.index)
    positions['BAC'] = stocks*signal['signals']
    portfoliox = positions['BAC'].multiply(data)

    pos_diff = positions['BAC'].diff()

    portfolio = pd.DataFrame()
    
    portfolio['Cartera'] = portfoliox
    portfolio['Cash'] = capital - (pos_diff.multiply(data).cumsum())
    portfolio['total'] = portfolio['Cash'] + portfolio['Cartera']
    portfolio['Returns'] = portfolio['total'].pct_change()[1:]

    portfolio['Returns'] = portfolio['Returns'][portfolio['Returns'] != 0]
    
    ### Metricas de backtest ###
     
    ## variables ##
    
    gains = 0
    ng = 0
    losses = 0
    nl = 0
    totalR = 0

    ## Calcular metricas de backtest ##

    Fcapital = capital
    for i in percentage:
        if(i>0):
            gains += i
            ng += 1
        else:
            losses += -(i) 
            nl += 1
            
        totalR = totalR + i
        
        cre = 1 + i/100 
        Fcapital = int(Fcapital*cre) # Net worth
        

    # Profit Factor #
    ProfitFactor = round(gains/losses,2)
        
    # Win Ratio #
    WinRatio = round(ng / (ng + nl) * 100,1)
    
    # Average Winner #
    avgGain = gains/ng
    maxR = max(percentage)
    maxR = str(round(maxR,2))
    
    # Average Loser #
    avgLoss = losses/nl
    maxL = min(percentage)
    maxL = str(round(maxL,2))
    
    # Expected Value #
    EV = totalR/len(percentage)
    
    # Ratio #
    ratio = round(ng/nl*100,1)
    
    # Profit / Loss ratio #
    ProLosR = round((gains/ng)/(losses/nl),2)
    
    # Batting average #
    if(ng > 0 or nl > 0):
        battingAvg = ng/(ng+1)
    else:
        battingAvg = 0
    
    adj = '(' + str(MAs) + '.' + str(MAl) + ')'
    
    def print_stats(): # imprimir metricas en consola
        print("\n" + "Total return over "+str(ng+nl)+ " trades: "+ str(round(totalR,2))+" %" + ", this leaves us a capital of: " + str(Fcapital) + " $")
        print("Setting:", adj)
        print("The profit factor is: " + str(ProfitFactor))
        print("The win ratio is: " + str(WinRatio)+" %")
        print("The expected value is: " + str(round(EV,2)))
        # print("Gain/loss ratio: "+ str(ratio) +"%")
        print("Profit/Loss ratio: "+ str(ProLosR)+":1")
        print("Average Gain: "+ str(round(avgGain,2))+"%")
        print("Average Loss: -"+ str(round(avgLoss,2))+"%")
        print("Max Return: "+ maxR+"%")
        print("Max Loss: "+ maxL+"%")
        print("Number of gains: " + str(ng))
        print("Number of losses: " + str(nl))
        print("Gains: " + str(round(gains,1)))
        print("Losses: " + str(round(losses,1)))
        
        print("Batting Avg: "+ str(round(battingAvg,2)))

    print_stats() # imprimir en la consola metricas de la estrategia 
     
    writer.writerow([adj, str(ng + nl), str(round(totalR,1)),str(Fcapital),str(ProfitFactor), str(round(WinRatio)), str(round(EV,2)), str(ProLosR), round(avgGain,2), round(avgLoss,2), ng, nl, x]) # imprimir metricas en el csv
    
    print(x) # ciclos hechos
    
    if MAs + 2 == MAl:
        MAs = 4
        MAl += 1
    x += 1
    
    MAs += 1

    # portfolio['market'] = data / data.shift(1)
    # portfolio['strategy'] = portfolio['total']/portfolio['total'].shift(1)
    # portfolio[['market','strategy']].cumprod().plot(grid=True)
    
    # plt.show()

endd = time.time()

print("\n")
print("# Diferents settings: ",x)
print("# Calculation timme of every setting: ",round((endd - startt) / x,1))

f.close()