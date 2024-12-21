from pyairtouch import AirTouchModel, connect, AirTouch
from flask import jsonify

async def airtouch_connect() -> AirTouch:
    airtouch = connect(AirTouchModel.AIRTOUCH_4, "192.168.1.104", 9004)
    if await airtouch.init():
        return airtouch
    print("Failed to connect to AirTouch")
    return None

async def get_zones():
    airtouch = await airtouch_connect()
    zones = {}
    zone_temps = {}

    for aircon in airtouch.air_conditioners:
        for zone in aircon.zones:
            zones[zone.name] = zone.current_damper_percentage
            if zone.has_temp_sensor:
                zone_temps[zone.name] = zone.current_temperature

    return jsonify({"zones": list(zones.keys()), "zone_percents": zones, "zone_temps": zone_temps}), 200

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