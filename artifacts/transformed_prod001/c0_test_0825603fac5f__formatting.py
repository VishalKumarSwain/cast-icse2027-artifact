import math

for _ in range(int(input())):
    n = int(input())
    a = list(map(int, input().split()))
    b = a[0]
    for i in a:
        b = math.gcd(b, i)
    print(n * b)
