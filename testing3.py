import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from numba import njit
from typing import List, Set, Tuple

def split_hi_lo_arr(bitmasks: List[Set[int]]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Splits bitmasks into hi, lo arrays for each set (64+ bits support)."""
    hi_list = []
    lo_list = []
    for s in bitmasks:
        arr = np.array(list(s))
        lo = arr & ((1 << 64) - 1)
        hi = arr >> 64
        hi_list.append(np.ascontiguousarray(hi, dtype=np.uint64))
        lo_list.append(np.ascontiguousarray(lo, dtype=np.uint64))
    return hi_list, lo_list

@njit(cache=True)
def candidate_mask(hi: np.uint64, lo: np.uint64, mask_hi: np.uint64, mask_lo: np.uint64):
    return (hi & mask_hi) == 0 and (lo & mask_lo) == 0

@njit(cache=True)
def count_combinations(hi_sets, lo_sets, idx, mask_hi, mask_lo):
    # Recursively search for valid combinations.
    if idx == len(hi_sets):
        return 1
    total = 0
    hi_arr = hi_sets[idx]
    lo_arr = lo_sets[idx]
    for i in range(hi_arr.shape[0]):
        if candidate_mask(hi_arr[i], lo_arr[i], mask_hi, mask_lo):
            total += count_combinations(
                hi_sets,
                lo_sets,
                idx+1,
                mask_hi | hi_arr[i],
                mask_lo | lo_arr[i])
    return total

def _worker_first_choice(args):
    hi_sets, lo_sets, first_idx = args
    hi0, lo0 = hi_sets[0][first_idx], lo_sets[0][first_idx]
    return count_combinations(
        hi_sets[1:], lo_sets[1:], 0, hi0, lo0)

def calculate_valid_combinations(sets: List[Set[int]]) -> int:
    hi_sets, lo_sets = split_hi_lo_arr(sets)
    first_len = len(hi_sets[0])
    # Prepare work: one job per first number
    jobs = [(hi_sets, lo_sets, idx) for idx in range(first_len)]
    # Use tqdm for progress bar
    with Pool(processes=max(1,min(cpu_count()-2, first_len))) as pool:
        results = []
        for res in tqdm(pool.imap_unordered(_worker_first_choice, jobs), total=first_len, desc="Solving..."):
            results.append(res)
    return sum(results)


def main():
    from testing import Board, CellState
    board = Board(10, 10, [6,4,4,3,3])
    bitmasks = board._generate_bitmasks(board._generate_valid_positions())
    sets = [set(bitmasks[ship_size]) for ship_size in board.ship_sizes]
    print("Total valid combinations:", calculate_valid_combinations(sets))

if __name__ == "__main__":
    import timeit
    number_of_runs = 1
    duration = timeit.timeit("main()", globals=globals(), number=number_of_runs)
    print(f"Average execution time over {number_of_runs} runs: {duration / number_of_runs:.5f} seconds")