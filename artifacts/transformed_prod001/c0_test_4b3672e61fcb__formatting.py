cases = int(input())
for _ in range(cases):
    count = 0
    a = []
    n = int(input())
    b = list(map(int, input().split()))
    b.sort()
    s = set(b)
    s = list(s)

    # Count the number of unique elements
    count = len(s)

    # Print the count
    print(count)
