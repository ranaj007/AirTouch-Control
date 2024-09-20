from pyairtouch import AirTouchModel, connect, api
from flask import Flask, jsonify, request
import asyncio

app = Flask(__name__)

@app.route("/control_airtouch", methods=["GET"])
def control_airtouch_route():
    zone_name = request.args.get('zone_name')
    try:
        temperature = float(request.args.get('temperature'))
    except ValueError:
        return jsonify({"error": "Temperature must be a number"}), 400

    if not zone_name:
        return jsonify({"error": "Zone name is required"}), 400
    
    if not temperature:
        return jsonify({"error": "Temperature is required"}), 400
    
    result = asyncio.run(control_airtouch(zone_name, temperature))
    return result


async def control_airtouch(zone_name, temperature):
    # Connect to AirTouch
    airtouch = connect(AirTouchModel.AIRTOUCH_4, "192.168.1.104", 9004)
    success = await airtouch.init()

    if not success:
        return jsonify({"error": "Failed to connect to AirTouch"}), 500
    
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")