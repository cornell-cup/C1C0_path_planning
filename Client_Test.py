from Networks.Client import *
from SensorCode import *
import time

if __name__ == "__main__":
    iterations = 1000
    robot = Client()
    sensor_state = SensorState()
    end_point = "(\'move forward\', 5.0)"
    robot.init_send_data({'end_point': end_point})
    start = time.time()
    print("Start Time:", start)
    for _ in range(iterations):
        sensor_state.update()
        robot.send_data(sensor_state.to_json())
    end = time.time()
    print("End Time:", end)
    print(f"{iterations} iterations: {end-start}")
