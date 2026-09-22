def max_reward(n_renamed):
    return sum(1.0 / i for i in range(1, n_renamed + 1))

n_renamed = int(input().strip())
print(f"{max_reward(n_renamed):.12f}")
