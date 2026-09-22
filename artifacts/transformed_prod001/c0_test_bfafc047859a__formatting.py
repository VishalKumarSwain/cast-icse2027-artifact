t = int(input())
for i in range(t):
    n = int(input())
    a = list(range(1, n + 1, 2))
    b = list(range(2, n + 1, 2))
    b.reverse()
    c = a + b
    print(*c)
