import asyncio
import os
import time

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from datetime import datetime, date, time

CHARGINGTH = 50
SLEEPTIME = 300
THEPLUG = "moped"
SLEEPTIME = 15 * 60 #in sec
LOGFILE = "askoll.csv"

EMAIL = os.environ.get('MEROSS_EMAIL') or "YOUR_MEROSS_CLOUD_EMAIL"
PASSWORD =  os.environ.get('MEROSS_PASS') or "YOUR_MEROSS_CLOUD_PASSWORD"

#EMAIL = os.environ.get('MEROSS_EMAIL') or "YOUR_MEROSS_CLOUD_EMAIL"
#PASSWORD = os.environ.get('MEROSS_PASSWORD') or "YOUR_MEROSS_CLOUD_PASSWORD"

async def ischarging(p):
	instant_consumption = await p.async_get_instant_metrics()
	activepower = instant_consumption.power
	if(activepower >= CHARGINGTH):
		print(f"Current consumption data: {instant_consumption}")
		return 1
	print(f"Current consumption data: {instant_consumption}")
	print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", activepower)
	return 0

async def get_day_powerconsumption(p, when):
	powerinfo = await p.async_get_daily_power_consumption()
	today = next(item for item in powerinfo if item["date"] == when)
	todaypower = today['total_consumption_kwh']
	return todaypower
	
async def turnoff_when_done(p):
	isw = await ischarging(p)
	while(isw):
		await asyncio.sleep(SLEEPTIME)
		isw = await ischarging(p)
	try:
		print("spengo")
		await p.async_turn_off()
	except:
		print("Impossibile spegnere alle " + str(datetime.now()))



async def main():	
	# Setup the HTTP client API from user-password
	http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)

	# Setup and start the device manager
	manager = MerossManager(http_client=http_api_client)
	await manager.async_init()

	await manager.async_device_discovery()
	plugs = manager.find_devices(device_name=THEPLUG)
	if not plugs == []:
		plug = plugs[0]

		starttime = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
		today = datetime.combine(datetime.now().date(), time.min)
		energystart = await get_day_powerconsumption(plug, today)

		f = open(LOGFILE, "a+")
		data = "{0},{1},".format(starttime,energystart)
		#print(data)
		f.write(data)
		f.close()
		await turnoff_when_done(plug)
		energyend = await get_day_powerconsumption(plug, today)
		stoptime = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
		f = open(LOGFILE, "a+")
		data = "{0},{1},{2}\n".format(stoptime,energyend,energyend-energystart)
		#print(data)
		f.write(data)
		f.close()

	 # Close the manager and logout from http_api
	manager.close()
	await http_api_client.async_logout()
	print(today, str(energyend-energystart))
	print("Finished")

if __name__ == '__main__':
	# On Windows + Python 3.8, you should uncomment the following
	# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
	loop.close()
