import numpy as np


def visualize_dict(dictionary):
    # Extract cell_numinates and values
    cell_nums = list(dictionary.keys())
    values = list(dictionary.values())

    if len(cell_nums) == 0:
        return

    # Determine the size of the matrix
    max_x = max(cell_nums, key=lambda x: x[0])[0]
    max_y = max(cell_nums, key=lambda x: x[1])[1]
    min_x = min(cell_nums, key=lambda x: x[0])[0]
    min_y = min(cell_nums, key=lambda x: x[1])[1]

    # Create a matrix filled with spaces
    matrix = np.full((max_y - min_y + 1, max_x - min_x + 1), ' ')

    # Normalize values to fit within the gradient range
    min_value = min(values)
    max_value = max(values)
    range_value = max_value - min_value

    # Define the gradient characters
    gradient = ".:-=+*#%@"

    def get_gradient_char(value):
        if range_value == 0:
            return gradient[-1]
        index = int((value - min_value) / range_value * (len(gradient) - 1))
        return gradient[index]

    # Fill the matrix with gradient characters based on normalized values
    for (x, y), value in dictionary.items():
        char = get_gradient_char(value)
        matrix[y - min_y, x - min_x] = char

    # Print the matrix
    for row in matrix:
        print(''.join(row))

    print()


def draw_board(cell_numinates):
    # Clear the screen
    print("\033[H\033[J", end="")

    # Draw the board
    for y in range(10):
        for x in range(10):
            if (x, y) in cell_numinates:
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


def generate_ship_positions(ships_details, board_size) -> list[dict[int, list[tuple[set[int], set[int], int]]]]:
    ship_positions = []
    for ship_details in ships_details:
        ship_name, ship_len, ship_count = ship_details
        for i in range(ship_count):
            ship_positions.append({})
            pos_id = 0
            for y in range(board_size[0]):
                for x in range(board_size[1]):

                    cell_num = coord_to_num((x, y), board_size)
                    ship_positions[-1][cell_num] = []

                    ship_coords = [(x+k, y) for k in range(ship_len)]
                    if within_board(ship_coords, board_size):

                        ship_nums = set([coord_to_num(coord, board_size)
                                        for coord in ship_coords])
                        padded_ship_coords = pad_ship(ship_coords, board_size)
                        padded_ship_nums = set(
                            [coord_to_num(coord, board_size) for coord in padded_ship_coords])

                        ship_positions[-1][cell_num].append(
                            (ship_nums, padded_ship_nums, pos_id))
                        pos_id += 1

                    ship_coords = [(x, y+k) for k in range(ship_len)]
                    if within_board(ship_coords, board_size):

                        ship_nums = set([coord_to_num(coord, board_size)
                                        for coord in ship_coords])
                        padded_ship_coords = pad_ship(ship_coords, board_size)
                        padded_ship_nums = set(
                            [coord_to_num(coord, board_size) for coord in padded_ship_coords])

                        ship_positions[-1][cell_num].append(
                            (ship_nums, padded_ship_nums, pos_id))
                        pos_id += 1

    return ship_positions


def recursion(ships_positions: list[dict[int, list[tuple[set[int], set[int], int]]]], cell_ranges: list[list[int]], redundancy_indices:list[int], pos_ids: list[int] = [], i: int = 0, board: set[int] = set([])) -> None:

    
    search_space = [cell_num for cell_num in cell_ranges[i] if cell_num not in board]
    # ships starting from cell with cell num
    for cell_num in search_space:
        # both x-axis and y-axis versions
        for ship, padded_ship, pos_id in ships_positions[i][cell_num]:
            
            if i in redundancy_indices and pos_ids[-1] >= pos_id:
                continue
                
            if padded_ship.isdisjoint(board):

                if i == len(ships_positions)-1:  # leaf condition

                    global densities
                    global k

                    for cell_num in board.union(ship):
                        densities[cell_num] += 1

                    if k % 10_000 == 0:
                        print("\033[H\033[J", end="")
                        print(pos_ids, end="\r")
                    k += 1
                    return

                else:

                    recursion(ships_positions, cell_ranges, redundancy_indices, pos_ids + [pos_id], i+1, board.union(ship))


ships = [("Schlachtschiff", 6, 1), ("Kreuzer", 4, 2),
         ("Zerstörer", 3, 3), ("UBoot", 2, 4)]

board_size = (10, 10)

ships_positions = generate_ship_positions(ships, board_size)

cell_ranges = [range(board_size[0]*board_size[1])]*len(ships_positions)

densities = {}
for i in range(board_size[0]*board_size[1]):
    densities[i] = 0

k = 0

# for ship_positions in ships_positions:
#     print()
#     for cell_num in ship_positions:
#         print(cell_num, ship_positions[cell_num])


recursion(ships_positions, cell_ranges, [2,4,5,7,8,9])
