def generate_valid_lists(input_list):
    n = len(input_list)
    valid_lists = []

    def is_valid(current_list, index):
        if input_list[index] == 1:
            if current_list[index] == 1:
                return False
            if index > 0 and current_list[index - 1] == 1:
                return False
            if index < n - 1 and current_list[index + 1] == 1:
                return False
        return True

    def backtrack(current_list, index):
        if index == n:
            valid_lists.append(current_list[:])
            return
        
        for digit in [0, 1]:
            current_list[index] = digit
            if is_valid(current_list, index):
                backtrack(current_list, index + 1)
            current_list[index] = 0  # backtrack

    # Start backtracking from the first position
    backtrack([0] * n, 0)

    return valid_lists

# Example usage:
input_list = [0, 1, 1, 1, 1, 0, 0, 1, 0, 1]
valid_lists = generate_valid_lists(input_list)

# Print all valid lists
for lst in valid_lists:
    print(lst)