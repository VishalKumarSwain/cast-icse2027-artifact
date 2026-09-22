t = int(input())
for i in range(t):
    n = int(input())
    b = []
    a = [int(i) for i in input().split()]
    for i in range(len(a)):
        if a[i] not in b:
            b += [a[i]]
    for i in range(len(b)):
        print(b[i], end=" ")
    print()
