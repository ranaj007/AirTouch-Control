from flask import Flask, jsonify, request
from multiprocessing import Process
import airtouch_monitor
import airtouch_cmds
import asyncio


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/api/get_zones", methods=["GET"])
def get_zones():
    result = asyncio.run(airtouch_cmds.get_zones())
    return result

@app.route("/api/set_zones", methods=["POST"])
def set_zones():
    zones = request.json
    zone_states = zones["zone_states"]
    zone_percents = zones["zone_percents"]
    result = asyncio.run(airtouch_cmds.set_zones(zone_states, zone_percents))
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
    asyncio.run(airtouch_monitor.main())

if __name__ == "__main__":
    p = Process(target=start_background_monitor)
    p.start()
    app.run(debug=True, host="0.0.0.0", port=5001)
    p.join()
