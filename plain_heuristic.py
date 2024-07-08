
from collections import deque
import numpy as np
import random
import math
import re
from itertools import combinations, product
import copy
import time

# Development
# optimizing ship size duplicates for lookup generation
# Inclusion-Exclusion-Principle for hit groups
# Board Generator for validation
# Human detection (AI)
# Backtracking for ingame
# GUI


class Board:

    # Shot status
    UNKNOWN = 0
    MISS = 1
    HIT = 2
    SUNK = 3

    def __init__(self, board_sizes: tuple[int], ship_sizes: list[int]):

        self.board_sizes = board_sizes
        self.ship_sizes = ship_sizes

        n_rows, n_cols = self.board_sizes

        self.board = np.zeros((n_rows, n_cols), dtype=np.uint8)

    def get_padding(self, ship_coords):

        n_rows, n_cols = self.board_sizes

        r_s = min(coord[0] for coord in ship_coords) - 1
        r_e = max(coord[0] for coord in ship_coords) + 2
        c_s = min(coord[1] for coord in ship_coords) - 1
        c_e = max(coord[1] for coord in ship_coords) + 2

        padding_coords = [(r, c) for r in range(r_s, r_e) for c in range(
            c_s, c_e) if (r, c) not in ship_coords and 0 <= r < n_rows and 0 <= c < n_cols]

        return padding_coords

    def get_placements_ss(self, ship_size, without_p=set(), without_padding=set()):

        placements = []

        n_rows, n_cols = self.board_sizes

        for row, col in zip(*np.where((self.board == Board.UNKNOWN) | (self.board == Board.HIT))):

            if col <= n_cols - ship_size:
                ship_coords = [(row, c)
                               for c in range(col, col + ship_size)]

                if all((self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.HIT) and (r, c) not in without_p for r, c in ship_coords) and any(self.board[r, c] == Board.UNKNOWN for r, c in ship_coords):

                    padding = self.get_padding(ship_coords)

                    if all((self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.MISS) and (r, c) not in without_padding for r, c in padding):

                        placements.append(set(ship_coords))

            if row <= n_rows - ship_size:
                ship_coords = [(r, col)
                               for r in range(row, row + ship_size)]

                if all((self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.HIT) and (r, c) not in without_p for r, c in ship_coords) and any(self.board[r, c] == Board.UNKNOWN for r, c in ship_coords):

                    padding = self.get_padding(ship_coords)

                    if all((self.board[r, c] == Board.UNKNOWN or self.board[r, c] == Board.MISS) and (r, c) not in without_padding for r, c in padding):

                        placements.append(set(ship_coords))

        return placements

    def get_placements(self, ship_sizes, without_p=set(), without_padding=set()):

        placements = {}
        for ship_size in ship_sizes:
            placements[ship_size] = self.get_placements_ss(
                ship_size, without_p, without_padding)

        return placements

    def N_p(self, placement):

        ship_sizes = self.ship_sizes.copy()
        ship_sizes.remove(len(placement))

        placements = self.get_placements(
            set(ship_sizes), without_p=placement, without_padding=placement)

        if len(ship_sizes) > 4:

            num = math.prod(len(placements[ss]) for ss in ship_sizes)

        else:

            num = 0

            def recursion(config, ship_cells):

                n = len(config)

                if n == len(ship_sizes):
                    nonlocal num
                    num += 1
                    return

                ship_size = ship_sizes[n]

                for p in placements[ship_size]:
                    check_cells = p.union(self.get_padding(p))

            # recursive part
            # place the first one
            # place the second only if no intersection with first one

            pass

        return num

    def get_hit_groups(self):

        # get hit cells
        rows, cols = np.where(self.board == Board.HIT)
        hit_cells = set(zip(rows, cols))

        # form hit groups
        def bfs(start_cell, cell_set):

            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            queue = deque([start_cell])
            group = []

            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    group.append(current)
                    # Check all orthogonal directions
                    for d in directions:
                        neighbor = (current[0] + d[0], current[1] + d[1])
                        if neighbor in cell_set and neighbor not in visited:
                            queue.append(neighbor)

            return group

        hit_groups = []

        visited = set()
        for cell in hit_cells:
            if cell not in visited:
                group = bfs(cell, hit_cells)
                hit_groups.append(group)

        return hit_groups

    def calculate_probability_density(self):

        probability_map = np.zeros(self.board_sizes)

        hit_groups = self.get_hit_groups()

        # I-E-P for hit groups

        for k in range(len(hit_groups)+1):

            sign = (-1)**k

            combs = combinations(hit_groups, k)

            for comb in combs:

                hit_cells = []
                for hit_group in comb:
                    hit_cells += hit_group
                hit_cells = set(hit_cells)

                # get all placements of all ship_sizes
                placements = self.get_placements(
                    set(self.ship_sizes), without_p=hit_cells, without_padding=hit_cells)

                # for every placement add N_p to probability map
                for ship_size, p_ss in placements.items():

                    ship_size_count = self.ship_sizes.count(ship_size)

                    for p in p_ss:

                        N_p = sign*self.N_p(p)*ship_size_count

                        for coord in p:
                            probability_map[coord] += N_p

        # rescale probability map to left percentage
        probability_map *= sum(self.ship_sizes) / \
            (np.sum(probability_map) + 10**(-30))

        self.probability_map = probability_map

    def best_possible_shot(self):

        m = 0
        best_shots = []

        n_rows, n_cols = self.board_sizes

        for row in range(n_rows):
            for col in range(n_cols):
                cell_value = self.board[row, col]
                if self.probability_map[row][col] > m and cell_value == Board.UNKNOWN:
                    m = self.probability_map[row][col]
                    best_shots = []
                if self.probability_map[row][col] == m and cell_value == Board.UNKNOWN:
                    best_shots.append((row, col))

        m = 0
        diags = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for shot in best_shots:
            n = 0
            for dir in diags:
                coord = (shot[0] + dir[0], shot[0] + dir[1])

                r, c = coord
                if 0 <= r < n_rows and 0 <= c < n_cols:
                    if self.board[coord] == Board.UNKNOWN:
                        n += 1
            if n < m:
                best_shots.remove(shot)

            if n > m:
                m = n

        return random.choice(best_shots)

    def update_board_value(self, cell, value):

        ship_size_counter = 0

        n_rows, n_cols = self.board_sizes

        row, col = cell

        if value == Board.MISS:
            self.board[row, col] = Board.MISS

        elif value == Board.HIT:
            self.board[row, col] = Board.HIT

            for a, b in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row+a, col+b
                if 0 <= r < n_rows and 0 <= c < n_cols:
                    self.board[r, c] = Board.MISS

            ship_size_counter = 1

        elif value == Board.SUNK:

            self.board[row, col] = Board.SUNK

            ship_size_counter = 1

            for a, b in [(a_-1, b_-1) for a_ in range(3) for b_ in range(3)]:
                r, c = row+a, col+b
                if 0 <= r < n_rows and 0 <= c < n_cols:
                    if self.board[r, c] == Board.UNKNOWN:
                        self.board[r, c] = Board.MISS
                    elif self.board[r, c] == Board.HIT:
                        ship_size_counter += self.update_board_value(
                            (r, c), Board.SUNK)

        return ship_size_counter

    def __str__(self):

        n_rows, n_cols = self.board_sizes

        string = ""
        for row in range(n_rows):
            for col in range(n_cols):
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

    def check_and_store_tuple(self, input_string, max_value):
        # Define regular expression patterns for various formats
        patterns = [
            # (int, int) with optional spaces
            r'^\(\s*(\d+)\s*,\s*(\d+)\s*\)$',
            r'^\s*(\d+)\s*,\s*(\d+)\s*$',       # int, int with optional spaces
            # [int, int] with optional spaces
            r'^\[\s*(\d+)\s*,\s*(\d+)\s*\]$',
            # {int, int} with optional spaces
            r'^\{\s*(\d+)\s*,\s*(\d+)\s*\}$'
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

    def start_game(self):

        k = 0

        n_rows, n_cols = self.board_sizes

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

            shot = self.check_and_store_tuple(shot, n_rows)

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

    def test_game(self, test_board, verbose=2):

        board = Board(self.board_sizes, self.ship_sizes.copy())

        _test_board = copy.deepcopy(test_board)

        k = 0

        while True:

            start = time.time()

            board.calculate_probability_density()
            k += 1

            if verbose == 0:
                print("Round num:", k, end="\r")

            else:
                print("\n Round num", k)

            if verbose > 1:
                print(board)  # print(np.round(board.probability_map,0))

            if len(board.ship_sizes) == 0:
                print("Took", k, "Rounds")
                return k

            shot = board.best_possible_shot()

            value = board.board[shot[0], shot[1]]
            if value != Board.UNKNOWN:
                print("Already known")
                break

            value = get_shot_value(_test_board, shot)

            ship_size = board.update_board_value(shot, value)

            if verbose > 0:
                print("Best shot:", shot)
                if value == Board.HIT:
                    print("Hit!")
                elif value == Board.MISS:
                    print("Miss!")
                elif value == Board.SUNK:
                    print("Sunk!")
                print("Remaining ships:", board.ship_sizes)
                print("Hit groups:", len(board.get_hit_groups()))

            if ship_size in board.ship_sizes:
                board.ship_sizes.remove(ship_size)

            if verbose > 0:
                print(f"round took {time.time() - start} seconds")


def get_shot_value(test_board, shot):

    value = Board.MISS

    for ship in test_board:
        if shot in ship:
            value = Board.HIT
            ship.remove(shot)
            if len(ship) == 0:
                value = Board.SUNK

    return value


# Constants
BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]  # Standard Battleship ship sizes

board = Board(BOARD_SIZES, SHIP_SIZES)

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


def get_average_round_num(test_board, N):
    average = 0
    for _ in range(N):
        average += board.test_game(test_board, verbose=0)

    return average/N


test_boards = [test_board1, test_board2, test_board3, test_board4, test_board5]

# for test_board in test_boards:

#     N = 5
#     average = get_average_round_num(test_board, N)
#     print(f"Took average of {average} rounds")

board.test_game(test_board1)
