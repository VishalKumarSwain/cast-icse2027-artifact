import math

def calculate_candies_left(n_renamed, t):
    for _ in range(t):
        if n_renamed % 2 == 0:
            n_renamed = n_renamed // 2
        else:
            n_renamed = (n_renamed + 1) // 2
        
        n_renamed = n_renamed - n_renamed // 4
    
    return n_renamed

q = int(input())

for _ in range(q):
    n_renamed, t = map(int, input().split())
    print(calculate_candies_left(n_renamed, t))
