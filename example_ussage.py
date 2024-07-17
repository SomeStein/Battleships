import random
from game import Board, get_average_round_num, print_placement

test_board1 = [[(4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)],
               [(0, 0), (1, 0), (2, 0), (3, 0)],
               [(6, 1), (7, 1), (8, 1), (9, 1)],
               [(1, 6), (1, 7), (1, 8)],
               [(3, 7), (4, 7), (5, 7)],
               [(7, 7), (8, 7), (9, 7)],
               [(0, 3), (0, 4)],
               [(2, 2), (3, 2)],
               [(7, 3), (7, 4)],
               [(9, 4), (9, 5)]]

test_board2 = [[(9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5)],
               [(0, 6), (0, 7), (0, 8), (0, 9)],
               [(6, 9), (7, 9), (8, 9), (9, 9)],
               [(1, 0), (2, 0), (3, 0)],
               [(2, 9), (3, 9), (4, 9)],
               [(5, 0), (6, 0), (7, 0)],
               [(0, 2), (1, 2)],
               [(0, 4), (1, 4)],
               [(2, 7), (3, 7)],
               [(8, 7), (9, 7)]]

test_board3 = [[(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2)],
               [(0, 8), (1, 8), (2, 8), (3, 8)],
               [(9, 3), (9, 4), (9, 5), (9, 6)],
               [(1, 4), (1, 5), (1, 6)],
               [(3, 4), (4, 4), (5, 4)],
               [(6, 9), (7, 9), (8, 9)],
               [(0, 0), (0, 1)],
               [(3, 6), (4, 6)],
               [(5, 0), (6, 0)],
               [(6, 6), (6, 7)]]

test_board4 = [[(4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7)],
               [(0, 4), (0, 5), (0, 6), (0, 7)],
               [(2, 4), (2, 5), (2, 6), (2, 7)],
               [(0, 2), (1, 2), (2, 2)],
               [(6, 2), (6, 3), (6, 4)],
               [(6, 6), (6, 7), (6, 8)],
               [(5, 0), (6, 0)],
               [(8, 0), (8, 1)],
               [(8, 3), (8, 4)],
               [(8, 6), (8, 7)]]

test_board5 = [[(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2)],
               [(2, 5), (2, 6), (2, 7), (2, 8)],
               [(5, 6), (5, 7), (5, 8), (5, 9)],
               [(4, 4), (5, 4), (6, 4)],
               [(9, 1), (9, 2), (9, 3)],
               [(9, 6), (9, 7), (9, 8)],
               [(0, 0), (0, 1)],
               [(0, 7), (0, 8)],
               [(3, 0), (4, 0)],
               [(7, 7), (7, 8)]]


test_boards = [test_board1, test_board2, test_board3, test_board4, test_board5]


def generate_board(board_sizes, ship_sizes):

    width, height = board_sizes

    while True:

        skip = False

        # pick starting point and direction for every ship
        dirs = [(0, 1), (1, 0)]
        pickable_points = [(r, c) for r in range(height) for c in range(width)]

        test_board = []
        for ss in ship_sizes:

            # pick direction
            dir = random.choice(dirs)

            # pick starting point
            if dir == (0, 1):
                _pickable_points = [(r, c)
                                    for r, c in pickable_points if c < width - ss]
            else:
                _pickable_points = [(r, c)
                                    for r, c in pickable_points if r < height - ss]

            if len(_pickable_points) == 0:
                skip = True
                break

            r, c = random.choice(_pickable_points)

            # create ship coords
            ship_coords = set([(r+x, c+y) for x in range(1 + dir[0]*(ss-1))
                               for y in range(1 + dir[1]*(ss-1))])

            # check for overlaps
            padded_ship_coords = set(
                [(r+x, c+y) for x in [-1, 0, 1] for y in [-1, 0, 1] for r, c in ship_coords])

            if any(not padded_ship_coords.isdisjoint(other) for other in test_board):
                skip = True

            if skip:
                break

            for coord in padded_ship_coords:
                if coord in pickable_points:
                    pickable_points.remove(coord)

            test_board.append(ship_coords)

        if skip:
            continue

        return test_board


# Constants
BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
# Standard Battleship ship sizes
SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]

# # Constants
# BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
# # Standard Battleship ship sizes
# SHIP_SIZES = [5, 4, 3, 3, 2]

board = Board(BOARD_SIZES, SHIP_SIZES)

# for test_board in test_boards:

#     get_average_round_num(board, test_board, 200)

# test_board = generate_board(BOARD_SIZES, SHIP_SIZES)

print_placement([coord for ship in test_board4 for coord in ship], (10, 10))

board.test_game(test_board4)


# print("\n")
# average = mx = mn = k = 0
# for k in range(1, 101):

#     # Constants
#     BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
#     # Standard Battleship ship sizes
#     SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]

#     board = Board(BOARD_SIZES, SHIP_SIZES)

#     test_board = generate_board(BOARD_SIZES, SHIP_SIZES)

#     # print_placement(
#     #     [coord for ship in test_board for coord in ship], BOARD_SIZES)

#     rounds = board.test_game(test_board, 0)

#     if mn == 0:
#         mn = rounds

#     if rounds < mn:
#         mn = rounds

#     if rounds > mx:
#         mx = rounds

#     average += rounds

#     print("\033[2K", end="\r")
#     print("\x1b[A", end="\r")
#     print("\033[2K", end="\r")

#     print(f"total games played: {k}, average: {
#           round(average/k, 4)}, max: {mx}, min: {mn}")
