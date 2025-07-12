import multiprocessing
import timeit
from enum import Enum, auto 
from tqdm import tqdm

class CellState(Enum):
    UNKNOWN = auto()
    MISS = auto()
    HIT = auto()
    SUNK = auto()

class Board:
    def __init__(self, width: int, height: int, ship_sizes: list[int]):
        self.width = width
        self.height = height
        self.ship_sizes = sorted(ship_sizes)[::-1]
        self.cells = [[CellState.UNKNOWN for _ in range(width)] for _ in range(height)]

    def edit_cell(self, x: int, y: int, state: CellState) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = state
    
    def analyze(self) -> list[list[float]]:
        """Analyze the board and return probability distribution for ship placements."""
        probability_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Generate valid positions for each ship size
        positions = self._generate_valid_positions()
        
        # Generate bitmasks for efficient overlap checking
        bitmasks = self._generate_bitmasks(positions)
        
        # Calculate probabilities using recursive placement
        initial_remaining_ships = self.ship_sizes
        for idx in tqdm(range(len(bitmasks[initial_remaining_ships[0]])), desc="Placing first ship"):
            bitmask = bitmasks[initial_remaining_ships[0]][idx]
            self._calculate_probabilities(
                initial_remaining_ships[1:], 
                bitmask, 
                [idx], 
                1, 
                positions, 
                bitmasks, 
                probability_board
            )
        
        # Normalize probabilities
        return self._normalize_probabilities(probability_board)
    
    def _generate_valid_positions(self) -> dict[int, list[list[tuple[int, int]]]]:
        """Generate all valid positions for each ship size."""
        positions = {}
        
        for ship_size in set(self.ship_sizes):
            positions[ship_size] = []
            
            for r in range(self.height):
                for c in range(self.width):
                    # Horizontal placement
                    if c + ship_size <= self.width:
                        positions[ship_size].append([(r, c + i) for i in range(ship_size)])
                    # Vertical placement
                    if r + ship_size <= self.height:
                        positions[ship_size].append([(r + i, c) for i in range(ship_size)])
            
            # Remove invalid positions (those overlapping with MISS or SUNK cells)
            for pos_index in range(len(positions[ship_size])-1, -1, -1):
                pos = positions[ship_size][pos_index]
                if any(self.cells[r][c] in [CellState.MISS, CellState.SUNK] for r, c in pos):
                    positions[ship_size].pop(pos_index)
        
        return positions
    
    def _generate_bitmasks(self, positions: dict[int, list[list[tuple[int, int]]]]) -> dict[int, list[int]]:
        """Generate bitmasks for each valid position for efficient overlap checking, with positive x/y padding (German no-touch rule)."""
        bitmasks = {}
        for ship_size, pos_list in positions.items():
            bitmasks[ship_size] = []
            for pos in pos_list:
                bitmask = 0
                for r, c in pos:
                    bitmask |= (1 << (r * self.width + c))
                    # Apply padding only in positive x/y directions (right, down, down-right)
                    for dr, dc in [(1, 0), (0, 1), (1, 1)]:
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < self.height and 0 <= cc < self.width:
                            bitmask |= (1 << (rr * self.width + cc))
                bitmasks[ship_size].append(bitmask)
        return bitmasks
    
    def count_valid_configurations(
        self, 
        current_mask: int,
        remaining_bitmasks: list[set[int]]
        ) -> int:

        if not remaining_bitmasks:
            return 1

        count = 0
        print(remaining_bitmasks)

        for bitmask in remaining_bitmasks[0]:

            new_current_mask = current_mask | bitmask # is already checked by recursion before

            new_remaining_bitmasks = []
            for s in remaining_bitmasks[1:]:
                filtered = {other_mask for other_mask in s if new_current_mask & other_mask == 0}
                new_remaining_bitmasks.append(filtered)

            #if any(len(s) == 0 for s in new_remaining_bitmasks):
            #    continue

            count += self.count_valid_configurations(new_current_mask, new_remaining_bitmasks)


        return count

    def _calculate_probabilities(
        self, 
        remaining_ships: list[int], 
        current_mask: int, 
        bitmask_indices: list[int], 
        depth: int,
        positions: dict[int, list[list[tuple[int, int]]]],
        bitmasks: dict[int, list[int]],
        probability_board: list[list[float]]
    ) -> None:
        """Recursively calculate probabilities for all valid ship configurations."""
        if not remaining_ships:
            # Reconstruct used positions from indices for final accumulation
            used_positions = []
            for ship_size, idx in zip(self.ship_sizes, bitmask_indices):
                used_positions.append(positions[ship_size][idx])
            for pos in used_positions:
                for r, c in pos:
                    probability_board[r][c] += 1
            return

        ship_size = remaining_ships[0]
        
        # Determine the starting index
        # Only use monotonic indices if the previous ship had the same size
        start_idx = 0
        if bitmask_indices:
            prev_ship_idx = len(bitmask_indices) - 1
            prev_ship_size = self.ship_sizes[prev_ship_idx]
            if prev_ship_size == ship_size:
                # Same size ship - use monotonic ordering to avoid duplicates
                start_idx = bitmask_indices[-1]
        
        for idx in range(start_idx, len(bitmasks[ship_size])):
            bitmask = bitmasks[ship_size][idx]
            if current_mask & bitmask == 0:
                new_mask = current_mask | bitmask
                self._calculate_probabilities(
                    remaining_ships[1:], 
                    new_mask, 
                    bitmask_indices + [idx], 
                    depth + 1,
                    positions,
                    bitmasks,
                    probability_board
                )
    
    def _normalize_probabilities(self, probability_board: list[list[float]]) -> list[list[float]]:
        """Normalize probabilities so the total sum equals the number of ship cells."""
        total_hits = sum(self.ship_sizes)
        total_configurations = sum(sum(row) for row in probability_board)
        
        if total_configurations > 0:
            scale = total_hits / total_configurations
            for r in range(self.height):
                for c in range(self.width):
                    probability_board[r][c] *= scale
        
        return probability_board
    
    def print_probability_board(self, prob_board: list[list[float]] = None) -> None:
        """Pretty-print the probability board with two decimal places."""
        if prob_board is None:
            prob_board = self.analyze()
        
        if type(prob_board[0][0]) == float:
            for row in prob_board:
                print(" ".join(f"{cell:5.2f}" for cell in row))
        else: 
            for row in prob_board:
                print(" ".join(f"{cell:5d}" for cell in row))

    @staticmethod
    def _worker_task(args):
        board_self, initial_ship_size, idx, positions, bitmasks, ship_sizes, width, height = args
        probability_board = [[0 for _ in range(width)] for _ in range(height)]

        bitmask = bitmasks[initial_ship_size][idx]
        board_self._calculate_probabilities(
            ship_sizes[1:], bitmask, [idx], 1,
            positions, bitmasks, probability_board
        )
        return probability_board

    def analyze_parallel(self) -> list[list[float]]:
        positions = self._generate_valid_positions()
        bitmasks = self._generate_bitmasks(positions)
        ship_sizes = self.ship_sizes
        width, height = self.width, self.height

        args_list = [
            (self, ship_sizes[0], idx, positions, bitmasks, ship_sizes, width, height)
            for idx in range(len(bitmasks[ship_sizes[0]]))
        ]

        with multiprocessing.Pool() as pool:
            results = list(tqdm(pool.imap_unordered(Board._worker_task, args_list), total=len(args_list), desc="Placing first ship"))

        # Aggregate results
        probability_board = [[0 for _ in range(width)] for _ in range(height)]
        for local_board in results:
            for r in range(height):
                for c in range(width):
                    probability_board[r][c] += local_board[r][c]

        # Normalize
        return probability_board #self._normalize_probabilities(probability_board)


def test_analyze():
    board = Board(10, 10, [6])
    bitmasks = board._generate_bitmasks(board._generate_valid_positions())
    current_mask = 0
    remaining_bitmasks = [set(bitmasks[ship_size]) for ship_size in board.ship_sizes]
    print(board.count_valid_configurations(current_mask, remaining_bitmasks))

    #prob_board = board.analyze_parallel()
    #board.print_probability_board(prob_board)

if __name__ == "__main__":
    number_of_runs = 1
    duration = timeit.timeit("test_analyze()", globals=globals(), number=number_of_runs)
    print(f"Average execution time over {number_of_runs} runs: {duration / number_of_runs:.5f} seconds")


# Optimization notes future work:
# - Use numpy for faster array operations.
# - Consider using Cython or Numba for performance-critical sections.
# - Implement dynamic filtering of valid bitmasks to reduce redundant calculations
# - use pairwise bitmasking to reduce redundant calculations.