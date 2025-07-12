import numpy as np
from numba import njit
from tqdm import tqdm
import timeit
from multiprocessing import Pool, cpu_count
from functools import partial

def sets_to_numpy(sets):
    # Convert each set to a numpy array of dtype uint32 or uint64
    return [np.array(list(s), dtype=np.uint64) for s in sets]

@njit
def count_combinations(sets, idx, current_mask):
    if idx == len(sets):
        return 1
    res = 0
    for num in sets[idx]:
        if (num & current_mask) == 0:
            res += count_combinations(sets, idx + 1, current_mask | num)
    return res

def process_chunk(first_nums, sets_np, idx_range):
    local_count = 0
    for first_num in first_nums:
        if (first_num & 0) == 0:  # always true, for illustrative consistency
            local_count += count_combinations(sets_np, 1, first_num)
    return local_count

def main():

    from testing import Board
    board = Board(8, 8, [6,4,4,3,3,3,2,2,2,2])
    bitmasks = board._generate_bitmasks(board._generate_valid_positions())
    sets = [set(bitmasks[ship_size]) for ship_size in board.ship_sizes]

    sets_np = sets_to_numpy(sets)
    num_first_set = len(sets_np[0])
    chunk_size = (num_first_set + cpu_count() - 1) // cpu_count()
    chunks = [sets_np[0][i:i+chunk_size] for i in range(0, num_first_set, chunk_size)]

    process_func = partial(process_chunk, sets_np=sets_np, idx_range=None)

    with Pool(cpu_count()) as pool:
        results = list(tqdm(pool.imap(process_func, chunks), total=len(chunks)))

    total = sum(results)
    print(f"Total valid combinations: {total}")

# ---- Usage Example ----

if __name__ == "__main__":
    
    number_of_runs = 1
    duration = timeit.timeit("main()", globals=globals(), number=number_of_runs)
    print(f"Average execution time over {number_of_runs} runs: {duration / number_of_runs:.5f} seconds")