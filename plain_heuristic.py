import numpy as np

import re

def check_and_store_tuple(input_string, max_value):
    # Define regular expression patterns for various formats
    patterns = [
        r'^\(\s*(\d+)\s*,\s*(\d+)\s*\)$',  # (int, int) with optional spaces
        r'^\s*(\d+)\s*,\s*(\d+)\s*$',       # int, int with optional spaces
        r'^\[\s*(\d+)\s*,\s*(\d+)\s*\]$',   # [int, int] with optional spaces
        r'^\{\s*(\d+)\s*,\s*(\d+)\s*\}$'    # {int, int} with optional spaces
    ]
    
    for pattern in patterns:
        match = re.match(pattern, input_string)
        if match:
            row, col = map(int, match.groups())
            
            # Check if row and col are within the specified range
            if 0 <= row < max_value and 0 <= col < max_value:
                return (row, col)
            else:
                print("Warning: Values are out of range.")
                return None

    print("Warning: The input string is not in the correct format.")
    return None

class Board:
   
   # Shot status
   UNKNOWN = 0
   MISS = 1
   HIT = 2
   
   def __init__(self, board_size, ship_sizes):
      
      self.board_size = board_size
      self.ship_sizes = ship_sizes
      
      self.board = [[self.UNKNOWN for _ in range(board_size)] for _ in range(board_size)]

   # Function to get possible ship placements
   def get_possible_placements(self, ship_size):
      
      placements = []

      # Horizontal placements
      for row in range(self.board_size):
         for col in range(self.board_size - ship_size + 1):
               if all(self.board[row][c] == self.UNKNOWN or self.board[row][c] == self.HIT for c in range(col, col + ship_size)):
                  placements.append([(row, c) for c in range(col, col + ship_size)])

      # Vertical placements
      for col in range(self.board_size):
         for row in range(self.board_size - ship_size + 1):
               if all(self.board[r][col] == self.UNKNOWN or self.board[r][col] == self.HIT for r in range(row, row + ship_size)):
                  placements.append([(r, col) for r in range(row, row + ship_size)])

      return placements

   # Function to calculate probability density map
   def calculate_probability_density(self):
      probability_map = np.zeros((self.board_size, self.board_size), dtype=np.uint8)

      for ship_size in self.ship_sizes:
         placements = self.get_possible_placements(ship_size)
         for placement in placements:
               for cell in placement:
                  probability_map[cell[0]][cell[1]] += 1

      return probability_map
   
   def best_possible_shot(self):
      probability_map = self.calculate_probability_density()
      m = 0 
      best_shot = (5,5)
      for col in range(self.board_size):
         for row in range(self.board_size):
            if probability_map[row][col] > m and self.board[row][col] != self.HIT:
               m = probability_map[row][col]
               best_shot = (row, col)
               
      return best_shot
               
               
   def start_game(self):
      while True:
         best_shot = self.best_possible_shot()
         print(self.calculate_probability_density())
         shot = input("\nBest possible shot is: " + str(best_shot) + "\nEnter shot: ")
         
         shot = check_and_store_tuple(shot, self.board_size)
         
         if not shot:
            continue
         
         while True:
            value = input("Miss or Hit?\n")
            
            if value in ["Miss", "miss", "m", "M"]:
               value = self.MISS
            elif value in ["Hit", "hit", "H", "h"]:
               value = self.HIT
            else:
               continue
            break
         
         self.board[shot[0]][shot[1]] = value
         
         if value == self.HIT:
            for a,b in [(1,1),(1,-1),(-1,1),(-1,-1)]:
               row = shot[0] + a
               col = shot[1] + b 
               if 0 <= row < self.board_size and 0 <= col < self.board_size:
                  self.board[row][col] = self.MISS
         
               
               
# Constants
BOARD_SIZE = 10  # Standard Battleship board size is 10x10
SHIP_SIZES = [6, 4, 4, 3, 3, 3, 2, 2, 2, 2]  # Standard Battleship ship sizes
      
board = Board(BOARD_SIZE, SHIP_SIZES)

board.start_game()

