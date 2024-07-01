
quarter = [[54, 77, 3, 23, 28],
 [77, 250, 196, 242, 237],
 [3,196,89, 130, 115],
 [23,242,130,191, 173],
 [28,237,115,173, 153]]



half = [e + e[::-1] for e in quarter]

whole = half + half[::-1]

import numpy as np

print()

whole = abs(np.array(whole)-255.0)/255.0 * 0.6 + 0.3

np.set_printoptions(linewidth=150)

print(whole)