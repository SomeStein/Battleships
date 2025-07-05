from enum import Enum, auto 

class CellState(Enum):
    UNKNOWN = auto()
    MISS = auto()
    HIT = auto()
    SUNK = auto()
    BLOCKED = auto()
    
class ShipDirection(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()
    
class Ship: 
    def __init__(self, size: int, dir: ShipDirection, pos: tuple[int, int]):
        self.size : int = size
        self.dir : ShipDirection = dir
        self.pos : tuple[int, int] = pos
        self.cells : list[tuple[int, int]] = []
        self.generate_cells()
        self.hits : int = 0
        self.sunk : bool = False
        
    def generate_cells(self) -> None:
        x, y = self.pos
        for i in range(self.size):
            if self.dir == ShipDirection.HORIZONTAL:
                self.cells.append((x + i, y))
            else:
                self.cells.append((x, y + i))

    def hit(self) -> None:
        self.hits += 1
        if self.hits >= self.size:
            self.sunk = True

class Board:
    def __init__(self, width: int, height: int, ship_sizes: list[int]):
        self.width = width
        self.height = height
        self.ship_sizes = ship_sizes
        self.cells = [[CellState.UNKNOWN for _ in range(width)] for _ in range(height)]
        self.ships = []

    def add_ships(self, ships: list[Ship]) -> None:
        for ship in ships:
            if self.can_place_ship(ship):
                self.ships.append(ship)
                for cell in ship.cells:
                    x, y = cell
                    self.cells[y][x] = CellState.UNKNOWN
    
    

