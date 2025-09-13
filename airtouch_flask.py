from flask import Flask, jsonify, request, render_template
import airtouch_monitor
import multiprocessing
import airtouch_cmds
import asyncio
import os

app = Flask(__name__, template_folder="airtouch_frontend/dist", static_folder="airtouch_frontend/dist/assets")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/get_zones", methods=["GET"])
def get_zones():
    zone_percents = {'Zone 1': 11}
    while 11 in zone_percents.values():
        zones = asyncio.run(airtouch_cmds.get_zones())
        zones["zone_states"] = {zone: zones["zone_states"][zone] == "ON" for zone in zones["zone_states"]}
        zone_percents = zones["zone_percents"]
    return jsonify(zones), 200

@app.route("/api/set_zones", methods=["POST"])
def set_zones():
    zones = request.json
    zone_states = zones["zone_states"]
    zone_states = {zone: "ON" if zone_states[zone] else "OFF" for zone in zone_states}
    zone_percents = zones["zone_percents"]
    zone_temp_modes = zones["zone_temp_modes"]
    result = asyncio.run(airtouch_cmds.set_zones(zone_states, zone_percents, zone_temp_modes))
    return result

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
    
    result = asyncio.run(airtouch_cmds.control_airtouch(zone_name, temperature))
    return result

@app.route("/set_vent", methods=["GET"])
def set_vent():
    zone_name = request.args.get('zone_name')
    damper_percentage = int(request.args.get('vent'))
    return asyncio.run(airtouch_cmds.set_damper(zone_name, damper_percentage))

def start_background_monitor():
    print("Starting Airtouch background monitor...")
    asyncio.run(airtouch_monitor.main())

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', True)
    print("Starting Flask server...")
    p = multiprocessing.Process(target=start_background_monitor)
    p.start()
    print("Background monitor started.")
    port = os.getenv("FLASK_PORT", 5000)
    app.run(host="0.0.0.0", port=port)
    p.join()
