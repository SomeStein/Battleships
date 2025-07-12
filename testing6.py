import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from numba import njit
from typing import List, Set, Tuple

def split_hi_lo_arr(bitmasks: List[Set[int]]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    hi_list = []
    lo_list = []
    for s in bitmasks:
        arr = np.array(list(s))
        lo = arr & ((1 << 64) - 1)
        hi = arr >> 64
        hi_list.append(np.ascontiguousarray(hi, dtype=np.uint64))
        lo_list.append(np.ascontiguousarray(lo, dtype=np.uint64))
    return hi_list, lo_list

def identify_ship_groups(ship_sizes: List[int]) -> List[Tuple[int, int]]:
    groups = []
    if not ship_sizes:
        return groups
    last_size = ship_sizes[0]
    start = 0
    for i, sz in enumerate(ship_sizes):
        if sz != last_size:
            groups.append((start, i - start))
            start = i
            last_size = sz
    groups.append((start, len(ship_sizes) - start))
    return groups

@njit(cache=True)
def candidate_mask(hi, lo, mask_hi, mask_lo):
    return (hi & mask_hi) == 0 and (lo & mask_lo) == 0

@njit(cache=True)
def count_combinations_with_groups(
    hi_sets, lo_sets, idx, mask_hi, mask_lo, groups, group_idx, min_indices
):
    if idx == len(hi_sets):
        return 1
    group_start, group_len = groups[group_idx]
    in_group_idx = idx - group_start
    min_index = min_indices[group_idx]
    hi_arr = hi_sets[idx]
    lo_arr = lo_sets[idx]
    total = 0
    for i in range(min_index, hi_arr.shape[0]):
        if candidate_mask(hi_arr[i], lo_arr[i], mask_hi, mask_lo):
            new_min_indices = min_indices.copy()
            if in_group_idx < group_len - 1:
                new_min_indices[group_idx] = i + 1  # next in group: strictly increasing
                next_group_idx = group_idx
            else:
                next_group_idx = group_idx + 1 if group_idx + 1 < len(groups) else group_idx
            total += count_combinations_with_groups(
                hi_sets,
                lo_sets,
                idx + 1,
                mask_hi | hi_arr[i],
                mask_lo | lo_arr[i],
                groups,
                next_group_idx,
                new_min_indices,
            )
    return total

def _worker_first_group_choice(args):
    hi_sets, lo_sets, groups, idx = args
    hi0, lo0 = hi_sets[0][idx], lo_sets[0][idx]
    min_indices = np.zeros(len(groups), dtype=np.int32)
    # For first group, we set the next minimum to idx+1:
    if groups[0][1] > 1:
        min_indices[0] = idx+1
    # We start at idx=1 since we've fixed the first ship of first group
    return count_combinations_with_groups(
        hi_sets[1:], lo_sets[1:], 0, hi0, lo0, groups, 0 if groups[0][1] == 1 else 0, min_indices
    )

def calculate_valid_combinations(sets: List[Set[int]], ship_sizes: List[int]) -> int:
    hi_sets, lo_sets = split_hi_lo_arr(sets)
    if len(hi_sets) == 1:
        return len(hi_sets[0])
    hi_sets_arr = [np.asarray(arr) for arr in hi_sets]
    lo_sets_arr = [np.asarray(arr) for arr in lo_sets]
    groups = identify_ship_groups(ship_sizes)
    n_first = len(hi_sets_arr[0])
    jobs = [(hi_sets_arr, lo_sets_arr, groups, idx) for idx in range(n_first)]
    num_processes = max(1, min(cpu_count()-2, n_first))
    with Pool(processes=num_processes) as pool:
        results = []
        for res in tqdm(pool.imap_unordered(_worker_first_group_choice, jobs), total=n_first, desc="Solving..."):
            results.append(res)
    return sum(results)

def main():
    from testing import Board
    board = Board(10, 10, [6, 4, 4, 4])
    bitmasks = board._generate_bitmasks(board._generate_valid_positions())
    sets = [set(bitmasks[ship_size]) for ship_size in board.ship_sizes]
    print("Total unique combinations:",
          calculate_valid_combinations(sets, board.ship_sizes))

if __name__ == "__main__":
    import timeit
    number_of_runs = 1
    duration = timeit.timeit("main()", globals=globals(), number=number_of_runs)
    print(f"Average execution time over {number_of_runs} runs: {duration / number_of_runs:.5f} seconds")