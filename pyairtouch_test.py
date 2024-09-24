import asyncio
import time

from pyairtouch import AirTouchModel, connect, api
count = 0

async def main() -> None:
    try:
        airtouch = connect(AirTouchModel.AIRTOUCH_4, "192.168.1.104", 9004)

        success = await airtouch.init()

        if not success:
            print("Failed to connect to AirTouch")
            return

        async def _on_ac_status_updated(ac_id: int) -> None:
            print(time.ctime())
            aircon = airtouch.air_conditioners[ac_id]
            print(
                f"AC Status  : {aircon.power_state.name} {aircon.mode.name}  "
                f"temp={aircon.current_temperature:.1f} set_point={aircon.target_temperature:.1f}"
            )

            for zone in aircon.zones:
                print(f"Zone Status: {zone.name:10} {zone.power_state.name:3}")
                if zone.has_temp_sensor:
                    print(f"temp={zone.current_temperature:.1f} set_point={zone.target_temperature:.1f}")
                else:
                    print("No temperature sensor")
                print(f"damper={zone.current_damper_percentage}")
                print()
        
        async def _on_zone_status_updated(zone_id: int) -> None:
            global count
            print(time.ctime())
            aircon = airtouch.air_conditioners[0]
            zone = aircon.zones[zone_id]
            count = 10
            count = min(count, 100)
            await zone.set_damper_percentage(count)
            print(f"Zone Status: {zone.name:10} {zone.power_state.name:3}")
            if zone.has_temp_sensor:
                print(f"temp={zone.current_temperature:.1f} set_point={zone.target_temperature:.1f}")
            else:
                print("No temperature sensor")
            print(f"damper={zone.current_damper_percentage}")

        print(time.ctime())
        # Subscribe to AC status updates:
        for aircon in airtouch.air_conditioners:
            #await aircon.set_power(api.AcPowerControl.TURN_ON)
            print(f"AC {aircon.ac_id} is {aircon.power_state}")
            aircon.subscribe(_on_ac_status_updated)

            for zone in aircon.zones:
                print(f"Zone Status: {zone.name:10} {zone.power_state.name:3}")
                # if zone.has_temp_sensor:
                #     print(f"temp={zone.current_temperature:.1f} set_point={zone.target_temperature:.1f}")
                # else:
                #     print("No temperature sensor")
                # print(f"damper={zone.current_damper_percentage}")
                # print(f"control method={zone.control_method}")
                # print()
                if zone.has_temp_sensor:
                    #zone.subscribe(_on_zone_status_updated)
                    print(f"temp={zone.current_temperature:.1f} set_point={zone.target_temperature:.1f}")
                else:
                    print("No temperature sensor")

                if zone.name == "Living" and False:
                    zone.subscribe(_on_zone_status_updated)
                    print(f"{zone.current_damper_percentage=}")
                    new_damper = 50 if zone.current_damper_percentage < 50 else 10
                    print(f"Setting Living damper to {new_damper}")
                    await zone.set_damper_percentage(new_damper)
                    print(f"{zone.current_damper_percentage=}")

            #aircon.subscribe(_on_ac_status_updated)

            # Print initial status
            #await _on_ac_status_updated(aircon.ac_id)

        # Keep the demo running for a few seconds
        await asyncio.sleep(60*60)
    finally:
        # Shutdown the connection
        await airtouch.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
