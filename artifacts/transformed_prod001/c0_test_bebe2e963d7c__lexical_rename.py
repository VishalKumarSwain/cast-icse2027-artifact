import sys

# Read input
n, k = map(int, sys.stdin.readline().split())
arr_renamed = list(map(int, sys.stdin.readline().split()))

# Calculate sum of parts
sum_of_parts = (n * (n + 1) // 2) - ((n - k) * (n - k + 1) // 2)

# Initialize variables
product_of_combs = 1
seen = False
counter = 0

# Iterate through the array
for i in arr_renamed:
    counter += 1
    if i > n - k:
        if seen:
            product_of_combs *= counter
            counter = 0
        seen = True
    else:
        seen = False

# Print the results
print(sum_of_parts, product_of_combs % 998244353)
