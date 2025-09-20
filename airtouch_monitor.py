from airtouch_cmds import airtouch_connect, do_temperature_control
from VictoriaMetrics import upload_data
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
        await do_temperature_control()
        
        airtouch = await airtouch_connect()

        unix_time_ms = int(time.time() * 1000)

        for aircon in airtouch.air_conditioners:
            aircon = airtouch.air_conditioners[0]

            send_data("power", "AirConditioner", unix_time_ms, int(aircon.power_state.name=="ON"))
            send_data("temperature", "AirConditioner", unix_time_ms, aircon.current_temperature)
            send_data("target_temperature", "AirConditioner", unix_time_ms, aircon.target_temperature)

            print(f"AC {aircon.ac_id} is {aircon.power_state}")

            print(f"Found {len(aircon.zones)} zones")
            for zone in aircon.zones:
                if not zone.has_temp_sensor:
                    continue
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

    finally:
        print("Closing connection")
        try:
            await airtouch.shutdown()
        except Exception:
            pass