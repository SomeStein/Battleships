import numpy as np

def visualize_dict(dictionary):
    # Extract coordinates and values
    coords = list(dictionary.keys())
    values = list(dictionary.values())

    if len(coords) == 0:
        return

    # Determine the size of the matrix
    max_x = max(coords, key=lambda x: x[0])[0]
    max_y = max(coords, key=lambda x: x[1])[1]
    min_x = min(coords, key=lambda x: x[0])[0]
    min_y = min(coords, key=lambda x: x[1])[1]

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

def draw_board(coordinates):
    # Clear the screen
    print("\033[H\033[J", end="")

    # Draw the board
    for y in range(10):
        for x in range(10):
            if (x, y) in coordinates:
                print("X", end="")
            else:
                print(".", end="")
        print()

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

def generate_ship_positions(ships, board_size):
    ship_positions = []
    padded_ships_positions = []
    for ship in ships:
        ship_name, ship_len, ship_count = ship
        for i in range(ship_count):
            ship_positions.append([])
            padded_ships_positions.append([])
            for x in range(board_size[0]):
                for y in range(board_size[1]):
                    ship = [(x+k, y) for k in range(ship_len)]
                    if within_board(ship, board_size):
                        ship = set(ship)
                        padded_ship = pad_ship(ship, board_size)
                        ship_positions[-1].append(ship)
                        padded_ships_positions[-1].append(padded_ship)
                    ship = [(x, y+k) for k in range(ship_len)]
                    if within_board(ship, board_size):
                        ship = set(ship)
                        padded_ship = pad_ship(ship, board_size)
                        ship_positions[-1].append(ship)
                        padded_ships_positions[-1].append(padded_ship)

    return ship_positions, padded_ships_positions


ships = [("Schlachtschiff", 6, 1), ("Kreuzer", 4, 2),
         ("Zerstörer", 3, 3), ("UBoot", 2, 4)]

board_size = (10, 10)

ships_positions, padded_ships_positions = generate_ship_positions(
    ships, board_size)

densities = {}
k = 0

def recursion(ships_positions, padded_ships_positions, densities, redundancy_indices, ship_indices=[], i=0, board=set([])):

    if i == len(ships_positions):

        for coord in board:
            densities[coord] = densities.setdefault(coord, 0) + 1
        global k
        if k % 100_000 == 0:
            draw_board(board)
            print(ship_indices)
            visualize_dict(densities)
            # Move the cursor back to the top left
            print("\033[H", end="")
        k += 1
        return

    if i in redundancy_indices:
        redundancy_start = ship_indices[-1] + 1
    else:
        redundancy_start = 0

    for j in range(redundancy_start, len(ships_positions[i])):
        ship = ships_positions[i][j]
        padded_ship = padded_ships_positions[i][j]
        if padded_ship.isdisjoint(board):
            recursion(ships_positions, padded_ships_positions, densities,
                      redundancy_indices, ship_indices + [j], i+1, board.union(ship))

recursion(ships_positions, padded_ships_positions,
          densities, [2, 4, 5, 7, 8, 9])
