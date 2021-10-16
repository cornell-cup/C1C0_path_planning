import math
import numpy as np

"""
Thoughts and considerations:
    Should we send motor powers alone, or motor powers and time to apply those powers?
    
    Does C1C0 stop immediately once the motor powers have been applied for a certain amount of time,
        or we do need to consider decelerating near the end point?

    Will the input mappings tell us both distance and direction when a unit of power is applied to the motors?
"""


class MotorPower:
    """
    Class that maps desired direction vector to real motor powers for left and right motors.
    Calculations are based on tested data from ECEs.
    Instance Attributes:
        left_map : list in form [left_x, left_y] where left_x/left_y is amount moved in x-direction/y-direction
         when left motor is given a unit of power
        right_map : list in form [right_x, right_y] where right_x/right_y is amount moved in x-direction/y-direction
         when right motor is given a unit of power
        vector : list in form [x, y] where x and y represent the vector we want C1C0 to move along (x^2 + y^2 = dist^2)
    """

    def __init__(self, left_map, right_map, vector):
        self.left_map = left_map
        self.right_map = right_map
        self.vector = vector

    """
    Method that computes [c1, c2] where c1/c2 are the weights (motor powers) that need to be assigned to the left
    and right motors in order to have C1C0 move properly along the desired vector.
    """

    def compute_combination(self):
        map_matrix = np.array([
            [self.left_map[0], self.right_map[0]],
            [self.left_map[1], self.right_map[1]]
        ])
        map_inv = np.linalg.inv(map_matrix)
        output = np.array([
            [self.vector[0]],
            [self.vector[1]]
        ])
        weights = map_inv.dot(output)
        return [weights[0][0], weights[1][0]]

    """
    This method requests data from sensor APIs to get mappings of x and y movements per unit of power for left 
    and right motors.
    """
    def retrieve_data(self):
        pass

    """
    This method sends back the necessary mapped weights for left and right motors in order to proceed along the desired 
    vector.
    """
    def send_mappings(self):
        pass
