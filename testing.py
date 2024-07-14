from game import Board

# Constants
BOARD_SIZES = 10, 10  # Standard Battleship board size is 10x10
SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]  # Standard Battleship ship sizes

board = Board(BOARD_SIZES, SHIP_SIZES)

# for test_board in test_boards:

# get_average_round_num(board, test_board, 200)

placements = board.get_placements()
ship_sizes = board.ship_sizes.copy()

n = len(ship_sizes)

placements = [placements[ss] for ss in ship_sizes]
ranges = [len(p_ss) for p_ss in placements]

placements = [p for p_ss in placements for p in p_ss]

ranges = [sum([l for l in ranges[:k]]) for k in range(1, n+1)]

overlaps = {}

for index1 in range(len(placements)):
    overlaps[index1] = set()
    for index2 in range(index1, len(placements)):
        if not placements[index1].isdisjoint(placements[index2]):
            overlaps[index1].add(index2)

index_list = [0] + list(ranges[:-1])


while True:

    index_list[-1] += 1

    i_check = n

    i_0 = n

    for i in range(n-1, 0, -1):
        index = index_list[i]
        if index == ranges[i]:
            index_list[i-1] += 1
            i_0 = i
            if i_check > i-1:
                i_check = i-1

    for j in range(i_0, n):
        index_list[j] = ranges[j-1]

    skip = False

    for i in range(i_check, n):
        index1 = index_list[i]
        for index2 in index_list[:i]:
            if index2 in overlaps[index1]:
                index_list[i] += 1
                i_check = i
                skip = True
                break

        if skip:
            break

    if skip:
        continue

    print(index_list)
