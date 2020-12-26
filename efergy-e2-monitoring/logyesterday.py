import numpy as np
import pandas as pd
import datetime
import os

WPATH = '/home/pi/Logs/'
#WPATH = './'
FILENAME = 'energy.csv'
SQLPATTERN = "insert into energy (ts,value) values ('{}', {});"

df = pd.read_csv(WPATH + FILENAME)
#data_e_ora prec(mm/h)  prec2(mm/h)     urel(%)   press(hPa)     temp(C)  temp2(C)  dir(gradi_da_nord)  dir2(gradi_da_nord)   vel(m/s)  vel2(m/s)  radG(W/m^2)  radN(W/m^2)
today = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time.min)
yesterday = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=1), datetime.time.min)

#df = df[['data','ora','watt']]
df['data_e_ora'] = df['data'] + ' ' + df['ora']

df['ts'] = df['data_e_ora'].apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S'))
df.set_index('ts')
df['hour'] = pd.DatetimeIndex(df['ts']).hour
df['min'] = pd.DatetimeIndex(df['ts']).minute


minutebase = df[(df['ts'] >= yesterday) & (df['ts'] < today)].groupby(['hour', 'min']).mean()
minutebase = minutebase.reset_index()
numrel = len(minutebase)

datey = yesterday.strftime("%Y-%m-%d").replace('-','')
fname = WPATH + datey + ".sql"
fout = open(fname, "w")
datey = yesterday.strftime("%Y-%m-%d")

for i in range(0, numrel):
    tsstr = datey + ' {:02d}'.format(int(minutebase.iloc[i][0])) + ':' + '{:02d}'.format(int(minutebase.iloc[i][1])) + ":00"
    row = [tsstr]
    row.extend([minutebase.iloc[i][2]])
    strSQL = SQLPATTERN.format(*row)
    fout.write(strSQL + "\n")
#    print(strSQL)

fout.close()
