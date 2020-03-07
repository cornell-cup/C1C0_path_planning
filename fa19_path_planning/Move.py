class Move:
    right = true
    multiplier = 1

    def__init__(self, dir, sens):
        self.direction = dir
        self.sensordist = sens

    def findRightDirection (self, dir, c, right):
        if self.sensordist > 1:
            self.direction = self.direction + dir
            return self.sensordist
        else:
            if (right)
