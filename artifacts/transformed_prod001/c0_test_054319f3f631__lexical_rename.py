from collections import defaultdict

s_renamed = input()
lens = len(s_renamed)
mod = 10**9 + 7

# Initialize the list to store possible remainders for each prefix
modl = [[] for i in range(lens)]
modl[0] = [i for i in range(10)]

# Calculate possible remainders for prefixes
for i in range(1, lens):
    modl[i] = [(modl[i-1][j]*10) % 13 for j in range(10)]

# Initialize the prefix count dictionary
upa = defaultdict(int)
upa[0] = 1

# Iterate over the string backwards
for i, char in enumerate(s_renamed[::-1]):
    newupa = defaultdict(int)
    if char != '?':
        # Update newupa for the current character
        for j in modl[i]:
            newupa[(j * int(char)) % 13] += upa[j]
    else:
        # Update newupa for all possible digits
        for j in range(10):
            for k in modl[i]:
                newupa[(k * j) % 13] += upa[k]
    upa = newupa

# Output the count of remainders 5 modulo the given mod
print(upa[5] % mod)
