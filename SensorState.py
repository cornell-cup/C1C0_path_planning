from typing import List, Dict


class SensorState:
    """
    Class to keep track of the state of the sensor inputs for C1C0
        Instance Attributes:
            lidar (List[tuple[int, int]]): List of lidar values, each element is an (ang,dist) tuple
            terabee_bot (List[int]): List of bottom terabee distances, each element is distance
            terabee_top (List[int]): List of top terabee distances, each element is distance
            pos_x (int): X position of hedgehog in GPS sub-map
            pos_y (int): Y position of hedgehog in GPS sub-map
        Class Attributes:
            terabee_bot_ang (Dict[int, int]): mapping from indices in terabee array's to angle of reading
            terabee_top_ang (Dict[int, int]): mapping from indices in terabee array's to angle of reading
    """
    terabee_bot_ang: Dict[int, int] = {}
    terabee_top_ang: Dict[int, int] = {}

    def __init__(self):
        self.lidar: List[tuple[int, int]] = []
        self.terabee_bot: List[int] = []
        self.terabee_top: List[int] = []
        self.pos_x: int
        self.pos_y: int

    def update(self) -> None:
        """
        Update function to read the serial lines and update the sensor state
        """
        pass



