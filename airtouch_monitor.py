from airtouch_cmds import airtouch_connect
from VictoriaMetrics import upload_data
import asyncio
import time

async def main() -> None:
    try:
        url = "http://192.168.1.100:8428/api/v1/import"
        async def _on_ac_status_updated(ac_id: int) -> None:
            #print(time.ctime())
            aircon = airtouch.air_conditioners[ac_id]
            #print(f"temp={aircon.current_temperature:.1f} set_point={aircon.target_temperature:.1f}")
            #print(f"AC Status  : {aircon.power_state.name} {aircon.mode.name}")
            #print()

            unix_time_ms = int(time.time() * 1000)

            data = {
                "metric": {
                    "__name__": "power",
                    "sender": "AirConditioner",
                    "application": "Airtouch_Custom_Sendor",
                },
                "values": [int(aircon.power_state.name=="ON")],
                "timestamps": [unix_time_ms],
                }

            upload_data(data, url)

            data = {
                "metric": {
                    "__name__": "temperature",
                    "sender": "AirConditioner",
                    "application": "Airtouch_Custom_Sendor",
                },
                "values": [aircon.current_temperature],
                "timestamps": [unix_time_ms],
                }

            upload_data(data, url)
                
        async def _on_zone_status_updated(zone_id: int) -> None:
            aircon = airtouch.air_conditioners[0]
            zone = aircon.zones[zone_id]

            if zone.current_damper_percentage == 11 or zone.target_temperature == 17:
                return
            
            zones[zone.name][1] = zone.current_damper_percentage
            zones[zone.name][2] = zone.target_temperature
            zones[zone.name][3] = zone.control_method.name

            print(f"{time.ctime()} : {zone.name}")
            print(f"Zone Status: {zone.name} {zone.power_state.name}")
            print(f"temp={zone.current_temperature} set_point={zone.target_temperature}")
            print(f"damper={zone.current_damper_percentage}")
            print('-----------------')
            print(zone.control_method.name)
            print(zone.control_method.value)
            print('-----------------')
            print()

            unix_time_ms = int(time.time() * 1000)

            data = {
                "metric": {
                    "__name__": "power",
                    "sender": zone.name,
                    "application": "Airtouch_Custom_Sendor",
                },
                "values": [int(zone.power_state.name=="ON")],
                "timestamps": [unix_time_ms],
                }

            upload_data(data, url)

            data = {
                "metric": {
                    "__name__": "temperature",
                    "sender": zone.name,
                    "application": "Airtouch_Custom_Sendor",
                },
                "values": [zone.current_temperature],
                "timestamps": [unix_time_ms],
                }

            upload_data(data, url)

            data = {
                "metric": {
                    "__name__": "damper",
                    "sender": zone.name,
                    "application": "Airtouch_Custom_Sendor",
                },
                "values": [zone.current_damper_percentage],
                "timestamps": [unix_time_ms],
                }

            upload_data(data, url)

            if zone.control_method.name == "TEMPERATURE":
                data = {
                "metric": {
                    "__name__": "target_temperature",
                    "sender": zone.name,
                    "application": "Airtouch_Custom_Sendor",
                },
                "values": [zone.target_temperature],
                "timestamps": [unix_time_ms],
                }

                upload_data(data, url)

        delay_s = 60
        zones = {}
        airtouch = await airtouch_connect()
        for aircon in airtouch.air_conditioners:
            print(f"AC {aircon.ac_id} is {aircon.power_state}")
            aircon.subscribe(_on_ac_status_updated)
            print(f"Found {len(aircon.zones)} zones")
            for zone in aircon.zones:
                if zone.has_temp_sensor:
                    print(f"Subscribing to {zone.name}")
                    zone.subscribe(_on_zone_status_updated)
                    zones[zone.name] = [zone, zone.current_damper_percentage, zone.target_temperature, zone.control_method.name]

        # Shutdown the connection
        #await airtouch.shutdown()

        while True:
            for zone_name in zones:
                zone = zones[zone_name][0]
                print(f"Pinging {zone.name}...")
                if zones[zone_name][3] == "DAMPER":
                    await zone.set_damper_percentage(11)
                    await asyncio.sleep(1)
                    await zone.set_damper_percentage(zones[zone_name][1])
                else:
                    await zone.set_target_temperature(17)
                    await asyncio.sleep(1)
                    await zone.set_target_temperature(zones[zone_name][2])
                await asyncio.sleep(1)
                print()
            
            #await airtouch.shutdown()
            await asyncio.sleep(delay_s)
    finally:
        print("Shutting down...")
        for zone_name in zones:
            zone = zones[zone_name][0]
            if zones[zone_name][3] == "DAMPER":
                await zone.set_damper_percentage(zones[zone_name][1])
            else:
                await zone.set_target_temperature(zones[zone_name][2])

        await airtouch.shutdown()