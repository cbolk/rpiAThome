import asyncio
import getpass
import json
import logging
import os
import ssl
import sys
import uuid as UUID
from hashlib import md5
from os import path, environ
from threading import Event
from zipfile import ZipFile
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import Namespace, OnlineStatus
from meross_iot.utilities.mqtt import build_device_request_topic, build_client_response_topic, build_client_user_topic


SNIFF_LOG_FILE = 'sniff.log'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
l = logging.getLogger().getChild("Sniffer")
l.setLevel(logging.DEBUG)
lhandler = logging.FileHandler(mode='w', filename=SNIFF_LOG_FILE)
lhandler.setFormatter(formatter)
l.addHandler(lhandler)

async def _main():
    print("Hello")
    email = 'cristiana.bolchini@gmail.com' #environ.get("MEROSS_EMAIL")
    password = 'pass4mero' #environ.get("MEROSS_PASS")
    devices = []
    http = None

    # Gather HTTP devices
    try:
        http = await MerossHttpClient.async_from_user_password(email, password)
        print("# Collecting devices via HTTP api...")
        devices = await http.async_list_devices()
    except:
        print("An error occurred while retrieving Meross devices.")
        exit(1)

    for i, d in enumerate(devices):
        print(f"[{i}] - {d.dev_name} ({d.device_type}) - {d.online_status.name}")

    while True:
        selection = input("Select the device you want to study (numeric index): ")
        selection = int(selection.strip())
        selected_device = devices[selection]
        if selected_device is not None:
            break

    print(f"You have selected {selected_device.dev_name}.")
    if selected_device.online_status != OnlineStatus.ONLINE:
        print("!! WARNING !! You selected a device that has not been reported as online. ")

    # Start the manager
    creds = http.cloud_credentials
    md5_hash = md5()
    clearpwd = "%s%s" % (creds.user_id, creds.key)
    md5_hash.update(clearpwd.encode("utf8"))
    hashed_password = md5_hash.hexdigest()
    # As very last step, try to collect data via get_all() and get_abilities
    l.info("--------------- More data -----------------")
    print("Collecting state info...")
    manager = None
    try:
        manager = MerossManager(http_client=http)
        await manager.async_init()

        # Manually get device abilities
        response_all = await manager.async_execute_cmd(destination_device_uuid=selected_device.uuid,
                                                       method="GET",
                                                       namespace=Namespace.SYSTEM_ALL,
                                                       payload={})
        response_abilities = await manager.async_execute_cmd(destination_device_uuid=selected_device.uuid,
                                                             method="GET",
                                                             namespace=Namespace.SYSTEM_ABILITY,
                                                             payload={})

        l.info(f"Sysdata for {selected_device.dev_name} ({selected_device.uuid}): {response_all}")
        l.info(f"Abilities for {selected_device.dev_name} ({selected_device.uuid}): {response_abilities}")
    except:
        l.exception(f"Could not collect sysdata/abilities for {selected_device.uuid}")
    finally:
        if manager is not None:
            manager.close()
        await http.async_logout()

    print("Collecting logs...")
    print(SNIFF_LOG_FILE)



def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main())
    loop.close()


if __name__ == '__main__':
    main()
