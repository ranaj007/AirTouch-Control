import asyncio
from pyairtouch import AirTouchModel, connect, AirTouch, api
from flask import jsonify
import json
import os

async def airtouch_connect() -> AirTouch:
    airtouch = connect(AirTouchModel.AIRTOUCH_4, "192.168.1.104", 9004)
    while not await airtouch.init():
        print("Failed to connect to AirTouch")
        print("Retrying connection in 5 seconds...")
        await asyncio.sleep(5)
    return airtouch


def load_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


async def do_temperature_control():
    airtouch = await airtouch_connect()
    
    temp_control = load_json_file("temp_control.json")

    for aircon in airtouch.air_conditioners:
        for zone in aircon.zones:
            if zone.name in temp_control and temp_control[zone.name]:
                print(f"Temp Control: Checking {zone.name}")
                if zone.current_temperature > zone.target_temperature:
                    new_damper = 0
                    print(f"Temp Control: Temperature reached in {zone.name}, closing damper")
                elif zone.target_temperature - zone.current_temperature < 0.5:
                    new_damper = 5
                elif zone.target_temperature - zone.current_temperature < 1:
                    new_damper = 10
                elif zone.target_temperature - zone.current_temperature < 2:
                    new_damper = 25
                else:
                    new_damper = 35
                
                if new_damper != zone.current_damper_percentage:
                    print(f"Temp Control: Setting {zone.name} damper to {new_damper}")
                    await zone.set_damper_percentage(new_damper)
                else:
                    print(f"Temp Control: {zone.name} no adjustment needed")


async def get_zones():
    airtouch = await airtouch_connect()
    zone_states = {}
    zone_percents = {}
    zone_temps = {}
    zone_temp_modes = {}

    temp_control = load_json_file("temp_control.json")

    for aircon in airtouch.air_conditioners:
        for zone in aircon.zones:
            zone_states[zone.name] = zone.power_state.name
            zone_percents[zone.name] = zone.current_damper_percentage
            if zone.has_temp_sensor:
                zone_temps[zone.name] = zone.current_temperature
                if zone.control_method.name in temp_control and temp_control[zone.name]:
                    zone_temp_modes[zone.name] = zone.target_temperature
                else:
                    zone_temp_modes[zone.name] = zone.target_temperature * -1

    return {
        "zones": list(zone_percents.keys()),
        "zone_states": zone_states,
        "zone_percents": zone_percents,
        "zone_temps": zone_temps,
        "zone_temp_modes": zone_temp_modes,
        }


async def set_zones(zone_states, zone_percents, zone_temp_modes):
    airtouch = await airtouch_connect()

    temp_control_file = "temp_control.json"
    temp_control = load_json_file(temp_control_file)

    for aircon in airtouch.air_conditioners:

        for zone in aircon.zones:
            if zone.name in zone_states:
                await zone.set_power(api.ZonePowerState[zone_states[zone.name]])

            if zone.name in zone_temp_modes: 
                if zone_temp_modes[zone.name] >= 16:
                    await zone.set_target_temperature(zone_temp_modes[zone.name])
                    temp_control[zone.name] = True
                else:
                    temp_control[zone.name] = False


            await zone.set_damper_percentage(zone_percents[zone.name])

    with open(temp_control_file, "w") as f:
        json.dump(temp_control, f)

    return jsonify({"message": "Set zones"}), 200


async def set_damper(zone_name, damper):
    airtouch = await airtouch_connect()

    for aircon in airtouch.air_conditioners:
        print(f"AC {aircon.ac_id} is {aircon.power_state}")

        for zone in aircon.zones:
            if zone.name == zone_name:
                await zone.set_damper_percentage(damper)
                return jsonify({"message": f"Set {zone_name} damper to {damper}"}), 200
    return jsonify({"error": f"Zone {zone_name} not found"}), 404


async def control_airtouch(zone_name, temperature):
    # Connect to AirTouch
    airtouch = await airtouch_connect()
    
    found_zone = False

    # Subscribe to AC status updates:
    for aircon in airtouch.air_conditioners:
        print(f"AC {aircon.ac_id} is {aircon.power_state}")

        for zone in aircon.zones:
            if zone.name == zone_name:
                #zone.subscribe(_on_zone_status_updated)
                found_zone = True
                new_damper = 50 if temperature < 25 else 10
                print(f"Setting {zone_name} damper to {new_damper}")
                await zone.set_damper_percentage(new_damper)

    if not found_zone:
        print(f"Zone {zone_name} not found in the following list:")
        for aircon in airtouch.air_conditioners:
            for zone in aircon.zones:
                print(zone.name)

        return jsonify({"error": f"Zone {zone_name} not found"}), 404
    return jsonify({"message": f"Set {zone_name} damper to {new_damper}"}), 200