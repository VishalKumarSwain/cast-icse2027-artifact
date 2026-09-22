def solve(a, b, k, boys, girls):
    boys.sort()
    girls.sort()
    dp_renamed = [[0] * (b + 1) for _ in range(a + 1)]
    dp_renamed[0][0] = 1
    res = 0
    for i in range(1, a + 1):
        for j in range(1, b + 1):
            dp_renamed[i][j] = dp_renamed[i - 1][j] + dp_renamed[i][j - 1]
            if i in boys and j in girls:
                res += dp_renamed[i - 1][j - 1]
    return res

t = int(input())
for _ in range(t):
    a, b, k = map(int, input().split())
    boys = list(map(int, input().split()))
    girls = list(map(int, input().split()))
    print(solve(a, b, k, boys, girls))
