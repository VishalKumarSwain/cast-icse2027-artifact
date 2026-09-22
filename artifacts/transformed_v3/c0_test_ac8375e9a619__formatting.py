monsters_killed = list(map(int, input().split()))
values = list(map(int, input().split()))
for _ in range(n - 1):
    a, b = map(int, input().split())
    print(sum(sorted(values[a - 1 : b])) // 1000000000)
    a, b = map(int, input().split())
    print(sum(sorted(monsters_killed[a - 1 : b])[::-1][:1000000]) // 1000000000)
