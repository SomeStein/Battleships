
def generate_valid_lists(input_list):
    n = len(input_list)
    valid_lists = []

    # Use a bitmask to represent valid configurations
    valid_masks = []

    # Initialize valid_masks based on the first element
    if input_list[0] == 0:
        valid_masks.append(1 << 0)  # Start with a configuration where the first element is 0
    elif input_list[0] == 1:
        valid_masks.append(1 << 1)  # Start with a configuration where the first element is 1

    # Iterate through each element of input_list
    for i in range(1, n):
        next_valid_masks = []

        if input_list[i] == 0:
            for mask in valid_masks:
                # Shift left and add valid configurations where current element is 0
                next_valid_masks.append((mask << 1) | 1)
        elif input_list[i] == 1:
            for mask in valid_masks:
                # Shift left and add valid configurations where current element is 1
                next_valid_masks.append(mask << 1)

        valid_masks.extend(next_valid_masks)

    # Convert valid_masks to valid_lists
    for mask in valid_masks:
        valid_list = []
        for j in range(n):
            if mask & (1 << j):
                valid_list.append(1)
            else:
                valid_list.append(0)
        valid_lists.append(valid_list)

    return valid_lists
   
import random
import time

start = time.time()
for i in range(1_000):
   stop = time.time()
   row = list(random.choices([0,1], k = 10))
   start += time.time() - stop
   print(generate_valid_lists(row))
print(time.time() - start)