from irobot_sdk.backend.bluetooth import Bluetooth
from irobot_sdk.robots import event, hand_over, Color, Robot, Root, Create3

backend = Bluetooth()
iRobot = Root(backend)

iRobot.play()