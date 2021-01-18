import asyncio
import os
import sys

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

EMAIL = os.environ.get('MEROSS_EMAIL') or "YOUR_MEROSS_CLOUD_EMAIL"
PASSWORD =  os.environ.get('MEROSS_PASS') or "YOUR_MEROSS_CLOUD_PASSWORD"
ALLPLUGS = "ALL"

async def main():

    if len(sys.argv) > 1:
        plugname = sys.argv[1];
    else:
        plugname = "ALL"
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the MSS310 devices that are registered on this account
    if plugname != ALLPLUGS:
        await manager.async_device_discovery()
        plug = manager.find_devices(device_name=plugname)
        if not plug == []:
            dev = plug[0]
            await dev.async_update()
        
            instant_consumption = await dev.async_get_instant_metrics()
            print(dev.name)
            print(f"Current consumption data: {instant_consumption}")
    else:
        await manager.async_device_discovery()
        plugs = manager.find_devices()
        for plug in plugs:
            dev = plug
        
            instant_consumption = await dev.async_get_instant_metrics()
            print(dev.name)
            print(f"Current consumption data: {instant_consumption}")



    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

if __name__ == '__main__':
    # On Windows + Python 3.8, you should uncomment the following
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
