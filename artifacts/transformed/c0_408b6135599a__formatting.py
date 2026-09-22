def largest_not_square(arr):
    non_squares = [x for x in arr if int(x**0.5) ** 2 != x]
    return max(non_squares)


# Driver code
n = int(input())
arr = list(map(int, input().split()))
print(largest_not_square(arr))
