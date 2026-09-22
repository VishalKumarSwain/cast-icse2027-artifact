MOD_renamed = 10**9 + 7

def comb(n, k, mod):
    if k > n:
        return 0
    k = min(k, n - k)
    numerator = 1
    for i in range(n, n - k, -1):
        numerator = numerator * i % mod
    denominator = 1
    for i in range(1, k + 1):
        denominator = denominator * i % mod
    return numerator * pow(denominator, mod - 2, mod) % mod

def solve(X, Y):
    ways = 0
    for a in range(0, X + 1, 2):
        b = (X - a) // 2
        if 2 * a + b == Y:
            ways = (ways + comb(a + b, a, MOD_renamed)) % MOD_renamed
    return ways

X, Y = map(int, input().split())
print(solve(X, Y))
