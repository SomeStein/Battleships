import numpy as np
import random

UNKNOWN, MISS, HIT, SUNK = 0, 1, 2, 3  # cell encoding for readability

# Directions for 4-way adjacency (up/down/left/right)
DIRS = [(0,1), (1,0), (0,-1), (-1,0)]

def is_valid_placement(board, ships, placement, n):
    # Given a potential complete placement, verify it covers all HITs, doesn't cover MISSes, or violate touch rule
    temp_board = np.copy(board)
    for idx, pos in enumerate(placement):
        for (x, y) in pos:  # each pos is list of coords
            if temp_board[x, y] == MISS:
                return False
            if temp_board[x, y] == SUNK and n > 1:  # sunk must be a single-cell ship unless explicitly stated
                return False
            # Place temporarily:
            temp_board[x, y] = 9 + idx  # arbitrary unique number for current ship

    # Diagonal touch check
    for pos in placement:
        for (x, y) in pos:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 10 and 0 <= ny < 10:
                        if temp_board[nx, ny] >= 9 and (nx, ny) not in pos:
                            if (dx, dy) != (0, 0):
                                return False
    # All hits covered?
    hit_positions = np.argwhere(board == HIT)
    for x, y in hit_positions:
        found = False
        for pos in placement:
            if (x, y) in pos:
                found = True
                break
        if not found:
            return False
    return True

def generate_random_placement(board, ships):
    n_ships = len(ships)
    tries = 10
    for attempt in range(tries):
        temp_board = np.copy(board)
        placement = []
        for s in ships:
            # Try possible positions for this ship
            possibilities = []
            for x in range(10):
                for y in range(10):
                    for dx, dy in [(0, 1), (1, 0)]:
                        cells = [(x + k*dx, y + k*dy) for k in range(s)]
                        # in bounds?
                        if all(0<=cx<10 and 0<=cy<10 for cx,cy in cells):
                            # check miss, sunk, overlap
                            if any(temp_board[cx, cy]==MISS or temp_board[cx, cy]>=9 for cx, cy in cells):
                                continue
                            # touching check
                            invalid = False
                            for cx, cy in cells:
                                for tx in [-1,0,1]:
                                    for ty in [-1,0,1]:
                                        nx, ny = cx+tx, cy+ty
                                        if 0<=nx<10 and 0<=ny<10:
                                            if temp_board[nx, ny]>=9 and (nx,ny) not in cells:
                                                invalid = True
                            if invalid: continue
                            # If passed, add
                            possibilities.append(cells)
            if not possibilities:
                break  # fail, try again
            choice = random.choice(possibilities)
            for cx, cy in choice:
                temp_board[cx, cy] = 9 + len(placement)  # unique id
            placement.append(choice)
        else:
            # succeeded!
            if is_valid_placement(board, ships, placement, n_ships):
                return placement
    return None  # failure

def probability_battleship_board(board, ships, n_samples=10000):
    """Returns a 10x10 array with probability of ship presence at each cell."""
    counts = np.zeros((10, 10), dtype=np.float32)
    valid_samples = 0
    for i in range(n_samples):
        placement = generate_random_placement(board, ships)
        if placement is None:
            continue
        valid_samples += 1
        for ship_cells in placement:
            for x, y in ship_cells:
                counts[x, y] += 1
    if valid_samples == 0:
        return counts
    return counts / valid_samples

# Example board state:
blank_board = np.zeros((10, 10), dtype=np.int8)
# # Add a known miss
# blank_board[2, 3] = MISS
# # Add a hit at (5,5)
# blank_board[5, 5] = HIT
# Example usage
prob_map = probability_battleship_board(blank_board, [6,4,4,3,3,3,2,2,2,2], n_samples=10000)
print(np.round(prob_map, 2))