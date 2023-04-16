import asyncio
import time

import nest_asyncio
from threading import Thread
# from Networks.Server import *
from SensorCode import SensorState
from irobot_sdk.backend.bluetooth import Bluetooth
from irobot_sdk.robots import event, hand_over, Color, Robot, Root, Create3

def run():
    global sensor_state
    global iRobot

    async def _update_speed():
        await iRobot.set_wheel_speeds(-0.15, 0.15)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        sensor_state.update()
        print(sensor_state.heading)
        loop.run_until_complete(_update_speed())

async def play():
    Thread(target=iRobot.play).start()
    time.sleep(5)
    Thread(target=run).start()

def run_play_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(play())
    loop.close()

if __name__ == "__main__":
    nest_asyncio.apply()
    backend = Bluetooth()
    iRobot = Create3(backend)
    setup_done = False
    Thread(target=run_play_async).start()
    sensor_state = SensorState(i_Robot=iRobot)
    # big_server = Server()
    # count = 1
    # while True:
    #     s = ServerGUI(big_server)
    #     s.server.send_update("path planning is over")
    #     with open("heading_data.txt", "w") as file:
    #         file.write(str(int(s.heading)) + "\n")
    #     # s.master.destroy()
    #     # print(count)
    #     count = count + 1