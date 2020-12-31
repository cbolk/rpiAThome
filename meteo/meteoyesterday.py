import numpy as np
import pandas as pd
import datetime
import os
import mariadb
import sys


WPATH = '/media/pi/Logs/meteo/'
#WPATH = './'
FILENAME = 'datiARPALo_502.csv'
DBNAME = 'monitoring'
DBTABLE = 'meteo'
DBUSER = 'usrmonitor'
DBPASS = DBUSER.replace('usr','pwd')
MISSINGVAL = -999.0

SQLPATTERN = "insert into " + DBTABLE + " (ts,prec,urel,press,temp,dir,vel,radG) values ('{}', {}, {}, {}, {}, {}, {}, {});"

try:
	conn = mariadb.connect(
		user=DBUSER,
		password=DBPASS,
		database=DBNAME,
		host="localhost",
		port=3306)
	cur = conn.cursor()

except mariadb.Error as e:
	print(f"Error connecting to MariaDB Platform: {e}")
	sys.exit(1)

df = pd.read_csv(WPATH + FILENAME)
#data_e_ora prec(mm/h)  prec2(mm/h)     urel(%)   press(hPa)     temp(C)  temp2(C)  dir(gradi_da_nord)  dir2(gradi_da_nord)   vel(m/s)  vel2(m/s)  radG(W/m^2)  radN(W/m^2)

yesterday = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=1), datetime.time.min)
yday = yesterday.strftime("%Y-%m-%d")
tday = datetime.date.today().strftime("%Y-%m-%d")
dsel = df[(df['data_e_ora']>=yday) & (df['data_e_ora']<tday)].copy()
dsel = dsel[['data_e_ora','prec(mm/h)','urel(%)','press(hPa)','temp(C)','dir(gradi_da_nord)','vel(m/s)','radG(W/m^2)']]

#replace -999.0 with NaN
ncol = len(dsel. columns)
for i in range(1, ncol):
    whereNaN = dsel[dsel[dsel.columns[i]] == MISSINGVAL].index
    dsel.at[whereNaN,dsel.columns[i]] = np.nan

dsel['ts'] = dsel['data_e_ora'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M'))
dsel.set_index('ts')
dsel['hour'] = pd.DatetimeIndex(dsel['ts']).hour

hourly = dsel.groupby('hour').mean()
hourly = hourly.reset_index()
numrel = len(hourly)

datey = yday.replace('-','')
for i in range(0, numrel):
    tsstr = yday + ' {:02d}'.format(int(hourly.iloc[i][0])) + ":00:00"
    row = [tsstr]
    for j in range(1, ncol):
    	row.extend([hourly.iloc[i][j]])
    strSQL = SQLPATTERN.format(*row)
    cur.execute(strSQL)
conn.commit()
conn.close()
