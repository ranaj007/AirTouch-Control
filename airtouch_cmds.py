from pyairtouch import AirTouchModel, connect, AirTouch

async def airtouch_connect() -> AirTouch:
    airtouch = connect(AirTouchModel.AIRTOUCH_4, "192.168.1.104", 9004)
    if await airtouch.init():
        return airtouch
    print("Failed to connect to AirTouch")
    return None