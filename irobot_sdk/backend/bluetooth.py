#
# Licensed under 3-Clause BSD license available in the License file. Copyright (c) 2022 iRobot Corporation. All rights reserved.
#

import sys

sys.path.insert(0, "C:/Users/huizh/PycharmProjects/irobot-sdk/root-robot-python-sdk")
if 'pyodide' in sys.modules:
    from irobot_sdk.backend.bluetooth_web import Bluetooth
else:
    from irobot_sdk.backend.bluetooth_desktop import Bluetooth
