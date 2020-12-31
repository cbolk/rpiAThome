import numpy as np
import pandas as pd
import datetime
import os
import mariadb
import sys

WPATH = '/home/pi/Logs/'
#WPATH = './'
FILENAME = 'energy.csv'
DBNAME = 'monitoring'
DBTABLE = 'energy'
DBUSER = 'usrmonitor'
DBPASS = DBUSER.replace('usr','pwd')
SQLPATTERN = "insert into " + DBTABLE + "(ts,value) values ('{}', {});"

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

dsel = df[df['data']==yesterday.strftime("%m/%d/%y")]

dsel['data_e_ora'] = dsel['data'] + ' ' + dsel['ora']

dsel['ts'] = dsel['data_e_ora'].apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S'))
dsel.set_index('ts')
dsel['hour'] = pd.DatetimeIndex(dsel['ts']).hour
dsel['min'] = pd.DatetimeIndex(dsel['ts']).minute


minutebase = dsel.groupby(['hour', 'min']).mean()
minutebase = minutebase.reset_index()
numrel = len(minutebase)

datey = yesterday.strftime("%Y-%m-%d")
print(str(numrel) + " readings")

for i in range(0, numrel):
    tsstr = datey + ' {:02d}'.format(int(minutebase.iloc[i][0])) + ':' + '{:02d}'.format(int(minutebase.iloc[i][1])) + ":00"
    row = [tsstr]
    row.extend([minutebase.iloc[i][2]])
    strSQL = SQLPATTERN.format(*row)
    cur.execute(strSQL)
    conn.commit()
conn.close()

