import numpy as np
import random
import math
import re


class Board:

    # Shot status
    UNKNOWN = 0
    MISS = 1
    HIT = 2
    SUNK = 3

    def __init__(self, board_sizes: tuple[int], ship_sizes: list[int]):

        self.board_sizes = board_sizes
        self.ship_sizes = ship_sizes

        self.board = np.zeros(
            (self.board_sizes[0], self.board_sizes[1]), dtype=np.uint8)

    def get_padding(self, ship_coords):

        r_s = ship_coords[0][0]-1
        r_e = ship_coords[-1][0]+2
        c_s = ship_coords[0][1]-1
        c_e = ship_coords[-1][1]+2
        bh = self.board_sizes[0]
        bw = self.board_sizes[1]

        padding_coords = [(r, c) for r in range(r_s, r_e) for c in range(
            c_s, c_e) if (r, c) not in ship_coords and 0 <= r < bh and 0 <= c < bw]

        return padding_coords

    def get_possible_placements(self, ship_size, valid_test=False):

        placements = []

        for row in range(self.board_sizes[0]):
            for col in range(self.board_sizes[1]):

                if col <= self.board_sizes[1] - ship_size:
                    ship_coords = [(row, c)
                                   for c in range(col, col + ship_size)]

                    if all(self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.HIT for r, c in ship_coords) and any(self.board[r, c] == Board.UNKNOWN for r, c in ship_coords):

                        padding = self.get_padding(ship_coords)

                        if all(self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.MISS for r, c in padding):

                            placements.append(ship_coords)

                if row <= self.board_sizes[0] - ship_size:
                    ship_coords = [(r, col)
                                   for r in range(row, row + ship_size)]

                    if all(self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.HIT for r, c in ship_coords):

                        padding = self.get_padding(ship_coords)

                        if all(self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.MISS for r, c in padding):

                            placements.append(ship_coords)

                if valid_test and len(placements) > 1:
                    return True

        return placements

    def calculate_probability_density(self):
        probability_map = np.zeros((self.board_sizes[0], self.board_sizes[1]))

        # get all possible placements of all ship_sizes
        # create N_ss number of placements for a ship size
        placements = []
        N_ss = []
        for ship_size in self.ship_sizes:
            placements_ss = self.get_possible_placements(ship_size)
            placements.append(placements_ss)
            N_ss.append(len(placements_ss))

        # create (index : indices of overlap) dictionary
        overlap_lookup = {}

        running_index_adder = 0

        for ship_num, placements_ss in enumerate(placements):

            for i, p in enumerate(placements_ss):

                index = i + running_index_adder
                check_cells = p + self.get_padding(p)
                overlap_lookup[index] = {}

                running_index_adder_2 = 0

                for ship_num_2, placements_ss_2 in enumerate(placements):

                    if ship_num != ship_num_2:

                        overlap_lookup[index][ship_num_2] = set()

                        for j, p_2 in enumerate(placements_ss_2):

                            index_2 = j + running_index_adder_2

                            for cell in p_2:
                                if cell in check_cells:

                                    overlap_lookup[index][ship_num_2].add(
                                        index_2)

                        N_index_ship_num = len(
                            overlap_lookup[index][ship_num_2])

                        overlap_lookup[index][ship_num_2] = N_index_ship_num

                    running_index_adder_2 += len(placements_ss_2)

            running_index_adder += N_ss[ship_num]

        def ship_num_from_index(index):

            running_total = 0
            for i, N in enumerate(N_ss):
                running_total += N
                if index < running_total:
                    return i

            return False

        # create N_p(index) function

        def N(index):

            # defaulting number with product of all lengths of placements
            ship_num = ship_num_from_index(index)

            num = 1

            for i in range(len(N_ss)):
                if i != ship_num:
                    num *= N_ss[i]

            num_overlaps = overlap_lookup[index]
            for key in num_overlaps:
                ship_nums = list(range(len(self.ship_sizes)))
                ship_nums.remove(ship_num)
                ship_nums.remove(key)

                print(ship_nums)

                subtract_num = 1

                for sn in ship_nums:
                    subtract_num *= N_ss[sn]

                subtract_num *= num_overlaps[key]

                print(num)

                num -= subtract_num

            print(num)

            return num
        N(0)

        return placements, N_ss, overlap_lookup

        # for every index add N(index)*placements[index] to probability map
        # rescale probability map to left percentage

        self.probability_map = probability_map

    def best_possible_shot(self):

        m = 0
        best_shots = []

        for row in range(self.board_sizes[0]):
            for col in range(self.board_sizes[1]):
                cell_value = self.board[row, col]
                if self.probability_map[row][col] > m and cell_value == Board.UNKNOWN:
                    m = self.probability_map[row][col]
                    best_shots = [(row, col)]
                if self.probability_map[row][col] == m and cell_value == Board.UNKNOWN:
                    best_shots.append((row, col))

        return random.choice(best_shots)

    def update_board_value(self, cell, value):

        ship_size_counter = 0

        row, col = cell

        if value == Board.MISS:
            self.board[row, col] = Board.MISS

        elif value == Board.HIT:
            self.board[row, col] = Board.HIT

            for a, b in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row+a, col+b
                if 0 <= r < self.board_sizes[0] and 0 <= c < self.board_sizes[1]:
                    self.board[r, c] = Board.MISS

            ship_size_counter = 1

        elif value == Board.SUNK:

            self.board[row, col] = Board.SUNK

            ship_size_counter = 1

            for a, b in [(a_-1, b_-1) for a_ in range(3) for b_ in range(3)]:
                r, c = row+a, col+b
                if 0 <= r < self.board_sizes[0] and 0 <= c < self.board_sizes[1]:
                    if self.board[r, c] == Board.UNKNOWN:
                        self.board[r, c] = Board.MISS
                    elif self.board[r, c] == Board.HIT:
                        ship_size_counter += self.update_board_value(
                            (r, c), Board.SUNK)

        return ship_size_counter

    def __str__(self):

        string = ""
        for row in range(self.board_sizes[0]):
            for col in range(self.board_sizes[1]):
                if self.board[row, col] == Board.HIT:
                    string += "⌷⌷⌷ "
                elif self.board[row, col] == Board.SUNK:
                    string += "███ "
                elif self.board[row, col] == Board.MISS:
                    string += "▒▒▒ "
                else:
                    num_str = str(
                        int(self.probability_map[row, col] * 100)) + "%"
                    string += num_str + " " * (4 - len(num_str))
            string += "\n"
        return string

    def start_game(self):

        k = 0

        while True:
            self.calculate_probability_density()
            k += 1
            best_shot = self.best_possible_shot()
            print("\nRound num:", k)
            print(self)
            print(self.ship_sizes)
            print("best shot", best_shot)
            shot = input("\nBest possible shot is: " +
                         str(best_shot) + "\nEnter shot: ")

            shot = check_and_store_tuple(shot, self.board_sizes[0])

            if not shot:
                continue
            value = self.board[shot[0], shot[1]]
            if value != Board.UNKNOWN:
                print("Already known")
                continue

            while True:
                value = input("Miss, Hit or SUNK?\n")

                if value in ["Miss", "miss", "m", "M"]:
                    value = Board.MISS
                elif value in ["Hit", "hit", "H", "h"]:
                    value = Board.HIT
                elif value in ["Sunk", "sunk", "S", "s"]:
                    value = Board.SUNK
                else:
                    continue
                break

            ship_size = self.update_board_value(shot, value)

            if ship_size >= 1 and value == Board.SUNK:
                self.ship_sizes.remove(ship_size)
                print(ship_size)

            if len(self.ship_sizes) == 0:
                break


def check_and_store_tuple(input_string, max_value):
    # Define regular expression patterns for various formats
    patterns = [
        r'^\(\s*(\d+)\s*,\s*(\d+)\s*\)$',  # (int, int) with optional spaces
        r'^\s*(\d+)\s*,\s*(\d+)\s*$',       # int, int with optional spaces
        r'^\[\s*(\d+)\s*,\s*(\d+)\s*\]$',   # [int, int] with optional spaces
        r'^\{\s*(\d+)\s*,\s*(\d+)\s*\}$'    # {int, int} with optional spaces
    ]

    for pattern in patterns:
        match = re.match(pattern, input_string)
        if match:
            row, col = map(int, match.groups())

            # Check if row and col are within the specified range
            if 0 <= row < max_value and 0 <= col < max_value:
                return (row, col)
            else:
                print("Warning: Values are out of range.")
                return None

    print("Warning: The input string is not in the correct format.")
    return None


def get_shot_value(test_board, shot):

    value = Board.MISS

    for ship in test_board:
        if shot in ship:
            value = Board.HIT
            ship.remove(shot)
            if len(ship) == 0:
                value = Board.SUNK

    return value


def find_furthest_coordinate(coords):
    # Calculate distances from the origin for each coordinate
    distances = [(x, y, math.sqrt(x**2 + y**2)) for x, y in coords]

    # Find the maximum distance
    max_distance = max(distances, key=lambda item: item[2])[2]

    # Collect all coordinates that have the maximum distance
    furthest_coords = [(x, y)
                       for x, y, dist in distances if dist == max_distance]

    # Select one coordinate at random if there are multiple
    return random.choice(furthest_coords)


def test_game(board_sizes, ship_sizes, test_board, verbose=2):

    board = Board(board_sizes, ship_sizes.copy())

    k = 0

    while True:

        import time

        # time.sleep(0.5)

        board.calculate_probability_density()
        k += 1

        print("\nRound num:", k)
        if verbose > 1:
            print(board)  # print(np.round(board.probability_map,0))
            print(board.ship_sizes)

        if len(board.ship_sizes) == 0:
            break

        shot = board.best_possible_shot()

        value = board.board[shot[0], shot[1]]
        if value != Board.UNKNOWN:
            print("Already known")
            break

        value = get_shot_value(test_board, shot)

        ship_size = board.update_board_value(shot, value)

        if verbose > 0:
            print("best shot", shot)
            print(ship_size)

        if ship_size in board.ship_sizes:
            board.ship_sizes.remove(ship_size)


# Constants
BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]  # Standard Battleship ship sizes

board = Board(BOARD_SIZES, SHIP_SIZES)

placements, N_ss, overlap_lookup = board.calculate_probability_density()

# for key in overlap_lookup:
#     print(key, ":", overlap_lookup[key])
