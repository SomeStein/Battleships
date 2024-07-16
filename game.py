
from collections import deque
import numpy as np
import random
import math
import re
from itertools import combinations, product
import copy
import time
import matplotlib.pyplot as plt

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

        return set(padding_coords)

    def valid_placement(self, ship_coords):

        if any(self.board[coord] in (Board.MISS, Board.SUNK) for coord in ship_coords):
            return False

        padding = self.get_padding(ship_coords)

        if any(self.board[coord] in (Board.HIT, Board.SUNK) for coord in padding):
            return False

        return any(self.board[coord] == Board.UNKNOWN for coord in ship_coords)

    def get_placements(self):

        n_rows, n_cols = self.board_sizes

        placements = {}

        coords = zip(*np.where((self.board == Board.UNKNOWN)
                               | (self.board == Board.HIT)))

        coords = [(int(r), int(c)) for r, c in coords]

        for ss in set(self.ship_sizes):

            placements[ss] = []

            for s_row, s_col in coords:

                if s_col + ss <= n_cols:

                    ship_coords = set([(s_row, c)
                                       for c in range(s_col, s_col + ss)])
                    if self.valid_placement(ship_coords):
                        placements[ss].append(ship_coords)

                if s_row + ss <= n_rows:

                    ship_coords = set([(r, s_col)
                                       for r in range(s_row, s_row + ss)])
                    if self.valid_placement(ship_coords):
                        placements[ss].append(ship_coords)

        return placements

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

    def get_indices(self, placements_list, filter):

        indices = {}

        for ss in set(self.ship_sizes):
            indices[ss] = set()

        # go through placements_list check which placements dont overlap with filter and add indices
        for index, p in enumerate(placements_list):
            if p.isdisjoint(filter):
                ss = len(p)
                indices[ss].add(index)

        return indices

    def N_p(self, ss, index, indices, overlaps, k_max):

        num = 1

        r_ship_sizes = self.ship_sizes.copy()
        r_ship_sizes.remove(ss)

        _indices = {}

        for r_ss in set(r_ship_sizes):

            ss_c = r_ship_sizes.count(r_ss)

            _indices[r_ss] = indices[r_ss] - overlaps[index, r_ss]

            num *= len(_indices[r_ss]) ** ss_c

        pairs = list(combinations(range(len(r_ship_sizes)), 2))

        sign = 1
        for k in range(1, k_max + 1):
            sign *= -1
            for comb in combinations(pairs, k):

                flat_comb = [i for pair in comb for i in pair]

                num += sign * math.prod(len(_indices[r_ship_sizes[i]])
                                        for i in range(len(r_ship_sizes)) if i not in flat_comb)

        return num

    def calculate_probability_density(self):

        probability_map = np.zeros(self.board_sizes)

        hit_groups = self.get_hit_groups()

        placements_dict = self.get_placements()

        placements_list = [p for p_ss in placements_dict.values()
                           for p in p_ss]

        if len(self.ship_sizes) > 0:

            value = m = 65
            n_pairs = math.comb(len(self.ship_sizes) - 1, 2)
            k_max = n_pairs + 1

            while value >= m:
                k_max -= 1
                value = sum([math.comb(n_pairs, k) for k in range(k_max)])

        else:

            k_max = 0

        # init overlaps
        overlaps = {}
        for index1, p1 in enumerate(placements_list):
            for ss in set(self.ship_sizes):
                overlaps[index1, ss] = set()

            padded_p1 = self.get_padding(p1).union(p1)
            for index2, p2 in enumerate(placements_list):
                if not padded_p1.isdisjoint(p2):
                    overlaps[index1, len(p2)].add(index2)

        # I-E-P for hit groups

        for k in range(len(hit_groups)+1):

            sign = (-1)**k

            combs = combinations(hit_groups, k)

            for comb in combs:

                hit_cells = {cell for hit_group in comb for cell in hit_group}

                indices = self.get_indices(placements_list, hit_cells)

                for ss in set(self.ship_sizes):

                    ss_c = self.ship_sizes.count(ss)

                    for index in indices[ss]:

                        N_p = self.N_p(ss, index, indices, overlaps, k_max)

                        for coord in placements_list[index]:
                            probability_map[coord] += sign * N_p * ss_c

        # rescale probability map to percentage
        probability_map *= (len(np.where(self.board == Board.SUNK)[0])+sum(self.ship_sizes)) / \
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
                if abs(self.probability_map[row][col] - m) < 0.1**6 and cell_value == Board.UNKNOWN:
                    best_shots.append((row, col))

        m = 0
        diags = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        # diags = [(r, c) for r in range(-1, 2) for c in range(-1, 2)]
        n_list = []
        for shot in best_shots:
            n = 0
            for dir in diags:

                r, c = (shot[0] + dir[0], shot[0] + dir[1])
                if 0 <= r < n_rows and 0 <= c < n_cols:
                    if self.board[r, c] == Board.UNKNOWN:
                        n += 1
            n_list.append(n)

        best_shots = [best_shots[i] for i in range(
            len(best_shots)) if n_list[i] == max(n_list)]

        return random.choice(best_shots)

    def update_board_value(self, cell, value):

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

        elif value == Board.SUNK:

            self.update_board_value(cell, Board.HIT)

            hit_groups = self.get_hit_groups()

            for hit_group in hit_groups:
                if cell in hit_group:
                    for hit_cell in hit_group:
                        self.board[hit_cell] = Board.SUNK

                    for coord in self.get_padding(hit_group):
                        self.board[coord] = Board.MISS

                    self.ship_sizes.remove(len(hit_group))

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
                if 0 < row <= max_value and 0 < col <= max_value:
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
            best_shot = best_shot[0] + 1, best_shot[1] + 1
            shot = input("\nBest possible shot is: " +
                         str(best_shot) + "\nEnter shot: ")

            shot = self.check_and_store_tuple(shot, n_rows)

            if not shot:
                continue

            shot = shot[0] - 1, shot[1] - 1

            value = self.board[shot[0], shot[1]]
            if value != Board.UNKNOWN:
                print("Already known")
                continue

            while True:
                value = input("Hit, Miss or Sunk?\n")

                if value in ["Miss", "miss", "m", "M"]:
                    value = Board.MISS
                elif value in ["Hit", "hit", "H", "h"]:
                    value = Board.HIT
                elif value in ["Sunk", "sunk", "S", "s"]:
                    value = Board.SUNK
                else:
                    continue
                break

            self.update_board_value(shot, value)

            if len(self.ship_sizes) == 0:
                break

    def test_game(self, test_board, verbose=2):

        start_time = time.time()

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
                data = board.probability_map
                plt.imshow(data, cmap='viridis', interpolation='nearest')
                # plt.show()

            if len(board.ship_sizes) == 0:
                if verbose > 0:
                    print(f"took {k} rounds and {
                        time.time() - start_time} seconds")
                return k

            shot = board.best_possible_shot()

            value = board.board[shot[0], shot[1]]
            if value != Board.UNKNOWN:
                print("Already known")
                break

            value = get_shot_value(_test_board, shot)

            board.update_board_value(shot, value)

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


def print_placement(placement, board_sizes):

    n_rows, n_cols = board_sizes

    string = "▒▒"*(n_cols+2)
    string += "\n"

    for row in range(n_rows):
        string += "▒▒"
        for col in range(n_cols):
            if (row, col) in placement:
                string += "██"
            else:
                string += "  "
        string += "▒▒"
        string += "\n"

    string += "▒▒"*(n_cols+2)

    print(string)


def get_average_round_num(board, test_board, N):

    average = 0
    mx = 0
    mn = math.prod(board.board_sizes)

    print("\n")
    for i in range(N):

        took = board.test_game(test_board, verbose=0)
        average += took

        if took > mx:
            mx = took
        if took < mn:
            mn = took

        print("\033[2K", end="\r")
        print("\x1b[A", end="\r")
        print("\033[2K", end="\r")

        print(f"{i+1} average: {round(average/(i+1), 4)}, max: {mx}, min: {mn}")

    return average/N
