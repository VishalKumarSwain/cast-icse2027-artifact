import math

t = int(input())

for _ in range(t):
    x, y, a, b = map(int, input().split())
    d = y - x
    g = math.gcd(a, b)

    if d % g != 0:
        print(-1)
    else:
        print((y - x) // g * b // g)
