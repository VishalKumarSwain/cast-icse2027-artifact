def largest_not_square(arr):
    non_squares_renamed = [x for x in arr if int(x**0.5)**2 != x]
    return max(non_squares_renamed)

# Driver code
n = int(input())
arr = list(map(int, input().split()))
print(largest_not_square(arr))
