from itertools import combinations
from game import Board, print_placement


# Constants
BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]  # Standard Battleship ship sizes

board = Board(BOARD_SIZES, SHIP_SIZES)

# Constants
BOARD_SIZES = 4, 4  # Standard Battleship board size is 10x10
SHIP_SIZES = [3, 2, 2]  # Standard Battleship ship sizes

board = Board(BOARD_SIZES, SHIP_SIZES)

placements = board.get_placements()

numbers = {}

for i, p1 in enumerate(placements[SHIP_SIZES[0]]):
    for j, p2 in enumerate(placements[SHIP_SIZES[1]]):
        for k, p3 in enumerate(placements[SHIP_SIZES[2]]):
            numbers[(i, j, k)] = 0

counts = {}

for i_1, i_2 in combinations(range(len(SHIP_SIZES)), 2):
    ss_1, ss_2 = SHIP_SIZES[i_1], SHIP_SIZES[i_2]
    for i, p1 in enumerate(placements[ss_1]):
        padded_p1 = p1.union(board.get_padding(p1))
        for j, p2 in enumerate(placements[ss_2]):
            if not padded_p1.isdisjoint(p2):
                k = 0
                for key in numbers:
                    if (key[i_1] == i and key[i_2] == j):
                        numbers[key] += 1
                        k += 1
print(numbers)
