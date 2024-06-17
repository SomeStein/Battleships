

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ship_coords = []

    def add_ship(self, coord_list):
        for (x, y) in coord_list:
            if 0 >= x or x > self.width or 0 >= y or y > self.height or (x, y) in self.ship_coords:

                print("Ship doesnt fit")
