import asyncio
import os

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

email = 'cristiana.bolchini@gmail.com' #environ.get("MEROSS_EMAIL")
password = 'pass4mero' #environ.get("MEROSS_PASS")

EMAIL = email #os.environ.get('MEROSS_EMAIL') or "YOUR_MEROSS_CLOUD_EMAIL"
PASSWORD =  password#os.environ.get('MEROSS_PASSWORD') or "YOUR_MEROSS_CLOUD_PASSWORD"


async def main():
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the MSS310 devices that are registered on this account

    plug = manager.find_devices(device_name="moped")
    if not plug == []:
        dev = plug[0]
        await dev.async_update()
    
        instant_consumption = await dev.async_get_instant_metrics()
        print(dev.name)
        print(f"Current consumption data: {instant_consumption}")

    await asyncio.sleep(10)
    plug = manager.find_devices(device_name="lamp")
    if not plug == []:
        dev = plug[0]
        await dev.async_update()
    
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
