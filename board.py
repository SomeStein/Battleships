

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ship_coords = []

    def add_ship(self, coord_list):
        for (x, y) in coord_list:
            if 0 >= x or x > self.width or 0 >= y or y > self.height or (x, y) in self.ship_coords:

                print("Ship doesnt fit")


# create Instance of a game
# game instance holds own board ship coords, water coords, hits and splashes as well as list of all possible boards filtered by hits and splashes.
NORMAL_GAME_MODE = 0
STREAK_GAME_MODE = 1
SALVES_GAME_MODE = 2


class Game:
    def __init__(self, board_sizes: tuple[int], ships: list[tuple[str, int]], game_mode: int = NORMAL_GAME_MODE):
        self.board_sizes = board_sizes
        self.ships = ships
        self.game_mode = game_mode
        self.SPLASH = 0
        self.HIT = 1
        self.possible_enemy_boards = self.generate_all_boards(
            self.board_sizes, self.ships, self.game_mode)

    def generate_all_boards(self):
        pass

    def update_enemy_board(coord, value):
        pass


ships = [("UBoot", 2), ("UBoot", 2), ("UBoot", 2), ("UBoot", 2), ("Zerstörer", 3),
         ("Zerstörer", 3), ("Zerstörer", 3), ("Kreuzer", 4), ("Kreuzer", 4), ("Schlachtschiff", 6)]

board_sizes = (10, 10)

game = Game(board_sizes, ships)

game.update_enemy_board((3, 2), game.HIT)

print(game)
