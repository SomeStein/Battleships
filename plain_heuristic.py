import numpy as np
import copy

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
   SUNK = 3
   
   def __init__(self, board_sizes: tuple[int], ship_sizes:list[int]):
      
      self.board_sizes = board_sizes
      self.ship_sizes = ship_sizes
      
      self.board = np.zeros((self.board_sizes[0], self.board_sizes[1]), dtype= np.uint8)
      
      self.num_all_placements = {}
      for ship_size in self.ship_sizes:
         num = len(self.get_possible_placements(ship_size))
         self.num_all_placements[ship_size] = num


   # Function to get possible ship placements
   def get_possible_placements(self, ship_size):
      
      placements = []

      # Horizontal placements
      for row in range(self.board_sizes[0]):                 
         for col in range(self.board_sizes[1] - ship_size + 1):
            if self.board[row,col] == Board.MISS:
               continue
            ship_coords = [(row, c) for c in range(col, col + ship_size)]
            
            padding_coords = []
            padding_coords += [(a-1,b) for a,b in ship_coords]
            padding_coords += [(a+1,b) for a,b in ship_coords]
            a,b = ship_coords[0]
            padding_coords += [(a-1,b-1) , (a,b-1) , (a+1, b-1)]
            a,b = ship_coords[-1]
            padding_coords += [(a-1,b+1) , (a,b+1) , (a+1, b+1)]
            
            valid = True
            for coord in ship_coords:   
               coord_value = self.board[coord[0],coord[1]]    
               if coord_value != Board.HIT and coord_value != Board.UNKNOWN:
                  valid = False
                  break
               
            for coord in padding_coords:
               a,b = coord
               if 0 <= a < self.board_sizes[0] and 0 <= b < self.board_sizes[1]:
                  coord_value = self.board[coord[0],coord[1]]    
                  if coord_value == Board.HIT or coord_value == Board.SUNK:
                     valid = False
                     break
                
            if valid:
               placements.append(ship_coords)           

      # Vertical placements
      for row in range(self.board_sizes[0] - ship_size + 1):         
         for col in range(self.board_sizes[1]):
            if self.board[row,col] == Board.MISS:
               continue
            ship_coords = [(r, col) for r in range(row, row + ship_size)]
            
            padding_coords = []
            padding_coords += [(a,b-1) for a,b in ship_coords]
            padding_coords += [(a,b+1) for a,b in ship_coords]
            a,b = ship_coords[0]
            padding_coords += [(a-1,b-1) , (a-1,b) , (a-1, b+1)]
            a,b = ship_coords[-1]
            padding_coords += [(a+1,b-1) , (a+1,b) , (a+1, b+1)]
            
            valid = True
            for coord in ship_coords:   
               coord_value = self.board[coord[0],coord[1]]    
               if coord_value != Board.HIT and coord_value != Board.UNKNOWN:
                  valid = False
                  break
               
            for coord in padding_coords:
               a,b = coord
               if 0 <= a < self.board_sizes[0] and 0 <= b < self.board_sizes[1]:
                  coord_value = self.board[coord[0],coord[1]]    
                  if coord_value == Board.HIT or coord_value == Board.SUNK:
                     valid = False
                     break
                
            if valid:    
               placements.append(ship_coords)

      return placements

   # Function to calculate probability density map
   def calculate_probability_density(self):
      probability_map = np.zeros((self.board_sizes[0], self.board_sizes[1]))

      for ship_size in self.ship_sizes:
         placements = self.get_possible_placements(ship_size)
         
         for placement in placements: 
         
            ship_sizes_copy = self.ship_sizes.copy()
            ship_sizes_copy.remove(ship_size)
            test_board = Board(self.board_sizes, ship_sizes_copy)
            
            test_board.board = self.board.copy()
            
            for coord in placement[:-1]:
               test_board.update_board_value(coord, Board.HIT)
            coord = placement[-1]
            test_board.update_board_value(coord, Board.SUNK)
               
            valid = True
            for test_ship_size in test_board.ship_sizes:
               if len(test_board.get_possible_placements(test_ship_size)) < 1:
                  valid = False
                  break
            if valid:
               
               points = self.num_all_placements[ship_size]/len(placements)
               for cell in placement:
                  if self.board[cell[0],cell[1]] == Board.HIT:
                     points += self.num_all_placements[ship_size]/len(placements)
                     
               for cell in placement:
                  cell_value = self.board[cell[0],cell[1]]
                  if cell_value != Board.SUNK and cell_value != Board.HIT:
                     probability_map[cell[0]][cell[1]] += points

      self.probability_map = probability_map
   
   def best_possible_shot(self):
      
      m = 0
      best_shot = (-1,-1)
      
      for row in range(self.board_sizes[0]):
         for col in range(self.board_sizes[1]):
            cell_value = self.board[row,col]
            if self.probability_map[row][col] > m and cell_value != Board.SUNK and cell_value != Board.HIT:
               m = self.probability_map[row][col]
               best_shot = (row, col)
               
      return best_shot
   
   def update_board_value(self, cell, value):
      
      
      ship_size_counter = 1
      
      row, col = cell 
      
      if value == Board.MISS:
         self.board[row,col] = Board.MISS
         
      elif value == Board.HIT:
         self.board[row,col] = Board.HIT
         
         for a,b in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            r,c = row+a, col+b  
            if 0 <= r < self.board_sizes[0] and 0 <= c < self.board_sizes[1]:
                  self.board[r,c] = Board.MISS
                  
      elif value == Board.SUNK:
         
         self.board[row,col] = Board.SUNK
         
         for a,b in [(a-1,b-1) for a in range(3) for b in range(3)]:
            r,c = row+a, col+b 
            if 0 <= r < self.board_sizes[0] and 0 <= c < self.board_sizes[1]:
               if self.board[r,c] == Board.UNKNOWN:
                  self.board[r,c] = Board.MISS
               elif self.board[r,c] == Board.HIT: 
                  ship_size_counter += self.update_board_value((r,c), Board.SUNK)
                  
      return ship_size_counter
   
   def __str__(self):
      
      string = ""
      for row in range(self.board_sizes[0]):
         for col in range(self.board_sizes[1]):
            if self.board[row,col] == Board.HIT or self.board[row,col] == Board.SUNK:
               string += "X   "
            elif self.board[row,col] == Board.MISS:
               string += "O   "
            else: 
               num_str = str(int(self.probability_map[row,col]))
               string +=  num_str + " "* (4 - len(num_str))
         string += "\n"
      return string
                      
               
   def start_game(self):
      
      k = 0 
      
      while True:
         self.calculate_probability_density()
         k += 1
         best_shot = self.best_possible_shot()
         print("\nRound num:", k)
         print(self)
         print(self.ship_sizes)
         print("best shot", best_shot)
         shot = input("\nBest possible shot is: " + str(best_shot) + "\nEnter shot: ")
         
         shot = check_and_store_tuple(shot, self.board_sizes[0])
         
         if not shot:
            continue
         value = self.board[shot[0],shot[1]]
         if value != Board.UNKNOWN:
            print("Already known")
            continue
         
         while True:
            value = input("Miss, Hit or SUNK?\n")
            
            if value in ["Miss", "miss", "m", "M"]:
               value = Board.MISS
            elif value in ["Hit", "hit", "H", "h"]:
               value = Board.HIT
            elif value in ["Sunk", "sunk", "S", "s"]:
               value = Board.SUNK
            else:
               continue
            break
         
         ship_size = self.update_board_value(shot, value)
         
         print(ship_size)
         
         if ship_size >= 1 and value == Board.SUNK: 
            self.ship_sizes.remove(ship_size)

         if len(self.ship_sizes) == 0:
            break
      
         
               
               
# Constants
BOARD_SIZES = 10,10  # Standard Battleship board size is 10x10
SHIP_SIZES = [6,4,4,3,3,3,2,2,2,2]  # Standard Battleship ship sizes
      
board = Board(BOARD_SIZES, SHIP_SIZES)


board.start_game()

