# # depth 9 has 68719476735 summands reducing to depth max_k to approximate number
# # max_k should be even to guarantee positive num
# max_k = 0

# # initial value for num of boards with placement p

# num = math.prod(len(p_placements[ss]) for ss in r_ship_sizes)

# # generate overlaps dict with ss index tuples as keys and lists of placement index tuples as values
# overlaps = {}
# for ss1, ss2 in combinations(r_ship_sizes, 2):
#     if (ss1, ss2) not in overlaps:
#         overlaps[ss1, ss2] = []
#         for a, p1 in enumerate(p_placements[ss1]):
#             padded_p1 = p1.union(self.get_padding(p1))
#             for b, p2 in enumerate(p_placements[ss2]):
#                 if not padded_p1.isdisjoint(p2):
#                     overlaps[ss1, ss2].append((a, b))

# # for k from 1 to max_k
# # get all combinations of size k from the keys of overlaps
# # for every combination get count of boards where those pairs overlap
# sign = 1
# for k in range(1, max_k+1):

#     sign *= -1

#     for comb in combinations(overlaps.keys(), k):
#         num += sign * count_valid_combinations(overlaps, comb)
