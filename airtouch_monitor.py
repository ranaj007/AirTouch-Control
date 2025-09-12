from airtouch_cmds import airtouch_connect
from VictoriaMetrics import upload_data
import asyncio
import time

def send_data(name: str, sender: str, unix_time_ms: int, value, url: str = "http://192.168.1.100:8428/api/v1/import") -> None:
    values = value if isinstance(value, list) else [value]

    data = {
        "metric": {
            "__name__": name,
            "sender": sender,
            "application": "Airtouch_Custom_Sendor",
        },
        "values": values,
        "timestamps": [unix_time_ms],
        }
    
    upload_data(data, url)


async def main() -> None:
    try:
        
        async def _on_ac_status_updated(ac_id: int) -> None:
            #print(time.ctime())
            aircon = airtouch.air_conditioners[ac_id]
            #print(f"temp={aircon.current_temperature:.1f} set_point={aircon.target_temperature:.1f}")
            #print(f"AC Status  : {aircon.power_state.name} {aircon.mode.name}")
            #print()

            unix_time_ms = int(time.time() * 1000)

            send_data("power", "AirConditioner", unix_time_ms, int(aircon.power_state.name=="ON"))
            send_data("temperature", "AirConditioner", unix_time_ms, aircon.current_temperature)
            send_data("target_temperature", "AirConditioner", unix_time_ms, aircon.target_temperature)

        async def _on_zone_status_updated(zone_id: int) -> None:
            aircon = airtouch.air_conditioners[0]
            zone = aircon.zones[zone_id]

            if zone.current_damper_percentage % 5 != 0 or zone.target_temperature == 17:
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

            send_data("power", zone.name, unix_time_ms, int(zone.power_state.name=="ON"))
            send_data("temperature", zone.name, unix_time_ms, zone.current_temperature)
            send_data("damper", zone.name, unix_time_ms, zone.current_damper_percentage)

            if zone.control_method.name == "TEMPERATURE":
                send_data("target_temperature", zone.name, unix_time_ms, zone.target_temperature)

        delay_s = 60*2 # 2 minutes
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
                    await zone.set_damper_percentage(99)
                    await asyncio.sleep(5)
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