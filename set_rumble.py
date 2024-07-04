from operator import pos
import numpy as np
import sys


def calculate_total_size(d):
    total_size = sys.getsizeof(d)  # Size of the dictionary itself

    for key, value_set in d.items():
        total_size += sys.getsizeof(key)  # Size of the key
        total_size += sys.getsizeof(value_set)  # Size of the set

        for value in value_set:
            # Size of each integer in the set
            total_size += sys.getsizeof(value)

    return total_size


def draw_board(pos_ids, ship_positions, board_size):
    # Clear the screen
    print("\033[H\033[J", end="")

    cell_nums = []

    for id in pos_ids:
        cell_nums += list(ship_positions[id][0])

    # Draw the board
    for y in range(board_size[1]):
        for x in range(board_size[0]):
            if coord_to_num((x, y), board_size) in cell_nums:
                print("X", end="")
            else:
                print(".", end="")
        print()


def coord_to_num(coord: tuple[int, int], board_size: tuple[int, int]) -> int:
    x, y = coord
    a, b = board_size
    return x+y*a


def num_to_coord(num: int, board_size: tuple[int, int]) -> tuple[int, int]:
    a, b = board_size
    return (num % a, num//b)


def within_board(ship, board_size):
    for x, y in ship:

        if x >= board_size[0]:
            return False
        if y >= board_size[1]:
            return False
        if x < 0:
            return False
        if y < 0:
            return False

    return True


def pad_ship(ship, board_size):
    padded_ship = set([])
    for (x, y) in ship:
        for a in [-1, 0, 1]:
            for b in [-1, 0, 1]:
                if within_board([(x+a, y+b)], board_size):
                    padded_ship.add((x+a, y+b))
    return padded_ship


def subtract_sets(list1, list2):
    return [s1 - s2 for s1, s2 in zip(list1, list2)]


def generate_ship_positions(ships_details, board_size) -> tuple[dict[int, tuple[set[int], set[int]]], list[set[int]]]:
    ship_positions = {}
    ship_positions["board_size"] = board_size
    ranges_int: list[int] = [0]
    pos_id = 0
    for ship_details in ships_details:
        ship_name, ship_len, ship_count = ship_details
        for i in range(ship_count):

            for y in range(board_size[0]):
                for x in range(board_size[1]):

                    ship_coords = [(x+k, y) for k in range(ship_len)]
                    if within_board(ship_coords, board_size):

                        ship_nums = set([coord_to_num(coord, board_size)
                                        for coord in ship_coords])
                        padded_ship_coords = pad_ship(ship_coords, board_size)
                        padded_ship_nums = set(
                            [coord_to_num(coord, board_size) for coord in padded_ship_coords])

                        ship_positions[pos_id] = (ship_nums, padded_ship_nums)
                        pos_id += 1

                    ship_coords = [(x, y+k) for k in range(ship_len)]
                    if within_board(ship_coords, board_size):

                        ship_nums = set([coord_to_num(coord, board_size)
                                        for coord in ship_coords])
                        padded_ship_coords = pad_ship(ship_coords, board_size)
                        padded_ship_nums = set(
                            [coord_to_num(coord, board_size) for coord in padded_ship_coords])

                        ship_positions[pos_id] = (ship_nums, padded_ship_nums)
                        pos_id += 1

            ranges_int.append(pos_id)

    ship_positions["ranges_int"] = ranges_int[:-1]

    total_num_ships = sum([num for (_a, _b, num) in ships_details])
    ranges_set_list = [set(range(ranges_int[i], ranges_int[i+1]))
                       for i in range(total_num_ships)]

    return ship_positions, ranges_set_list


def generate_filter_lookup(ship_positions: dict[int, tuple[set[int], set[int]]], ranges: list[tuple[int, int]]) -> dict[int, list[set[int]]]:

    filter_lookup: dict[int, list[set[int]]] = {}

    for i in range(len(ranges)):
        for id in ranges[i]:
            filter_lookup[id] = []
            padded_ship = ship_positions[id][1]
            for j in range(i+1, len(ranges)):
                filter_lookup[id].append(set())
                for other_id in ranges[j]:
                    other_ship = ship_positions[other_id][0]
                    if not padded_ship.isdisjoint(other_ship):
                        filter_lookup[id][-1].add(other_id)

    return filter_lookup


k = 0


def recursion(ship_positions: dict[int, set[int]], filter_lookup: dict[int, set[int]], ranges: list[set[int]], redundancy: dict[int, set[int]], pos_ids: list[int] = []) -> None:

    if len(ranges) == 0:  # base case
        global k
        k += 1
        if k % 1_000_000 == 0:
            draw_board(pos_ids, ship_positions, ship_positions["board_size"])
            ranges_int = ship_positions["ranges_int"]
            scaled_pos_ids = [a-b for (a, b) in zip(pos_ids, ranges_int)]
            print(scaled_pos_ids)
            print("\033[H", end="")

        return

    for id in sorted(list(ranges[0])):

        ranges_filter = filter_lookup[id]
        _ranges = subtract_sets(ranges[1:], ranges_filter)

        recursion(ship_positions, filter_lookup,
                  _ranges, redundancy, pos_ids + [id])

        ship_num = len(pos_ids)
        if ship_num in redundancy:
            for index in redundancy[ship_num]:
                ranges[index] - {id}


ships = [("Schlachtschiff", 6, 1), ("Kreuzer", 4, 1),
         ("Zerstörer", 3, 2), ("UBoot", 2, 1)]

board_size = (10, 10)

ship_positions, ranges = generate_ship_positions(ships, board_size)

filter_lookup = generate_filter_lookup(ship_positions, ranges)

redundancy = {1: {1}, 3: {1, 2}, 4: {1}, 6: {1, 2, 3}, 7: {1, 2}, 8: {1}}
redundancy = {}
recursion(
    ship_positions, filter_lookup, ranges, redundancy)
