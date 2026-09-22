import math


def calculate_candies_left(n, t):
    for _ in range(t):
        if n % 2 == 0:
            n = n // 2
        else:
            n = (n + 1) // 2

        n = n - n // 4

    return n


q = int(input())

for _ in range(q):
    n, t = map(int, input().split())
    print(calculate_candies_left(n, t))
