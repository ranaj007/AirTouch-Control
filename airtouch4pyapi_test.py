import asyncio
from airtouch4pyapi import AirTouch, AirTouchStatus

def print_groups(groups):
    for group in groups:
        print(f"Group Name: {group.GroupName:15s} Group Number: {group.GroupNumber:3d} PowerState: {group.PowerState:3s} IsOn: {group.IsOn} OpenPercent: {group.OpenPercent:3d} Temperature: {group.Temperature:3.1f} Target: {group.TargetSetpoint:3.1f} BelongToAc: {group.BelongsToAc:2d} Spill: {group.Spill}")


def print_acs(acs):
    for ac in acs:
        print(f"AC Name: {ac.AcName:15s} AC Number: {ac.AcNumber:3d} IsOn: {ac.IsOn} PowerState: {ac.PowerState:3s} Target: {ac.AcTargetSetpoint:3.1f} Temp: {ac.Temperature:3.1f} Modes Supported: {ac.ModeSupported} Fans Supported: {ac.FanSpeedSupported} startGroup: {ac.StartGroupNumber: 2d} GroupCount: {ac.GroupCount:2d} Spill: {ac.Spill}")

async def updateInfoAndDisplay(ip) -> asyncio.coroutines:
    at = AirTouch(ip)
    await at.UpdateInfo()
    if(at.Status != AirTouchStatus.OK):
        print("Got an error updating info.  Exiting")
        return
    print("Updated Info on Groups (Zones) and ACs")
    print("AC INFO")
    print("----------")
    acs = at.GetAcs()
    print_acs(acs)
    print("----------\n\n")
    print("GROUP/ZONE INFO")
    print("----------")
    groups = at.GetGroups()
    print_groups(groups)

    
#    await at.TurnAcOff(0)
#    print("Turned off ac 0, sleeping 4")
#    time.sleep(4);
    await at.TurnAcOn(0)
    print("Turned on ac 0")
#    print(at.GetSupportedFanSpeedsByGroup(0))
#    await at.SetGroupToPercentByGroupName("Zone 1", 5)

if __name__ == '__main__':
    ip_address = "192.168.1.104"
    asyncio.run(updateInfoAndDisplay(ip_address))
    