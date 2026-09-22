def max_reward(n):
    return sum(1.0 / i for i in range(1, n + 1))


n = int(input().strip())
print(f"{max_reward(n):.12f}")
