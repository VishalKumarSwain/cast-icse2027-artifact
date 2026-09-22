from sys import maxsize


def max_jump_reach(data):
    n = len(data)
    jump_reach = [1] * n
    max_reach = 0

    for i in range(1, n):
        for j in range(max_reach, i, -1):
            if data[j - 1] < data[i - 1]:
                jump_reach[i] = max(jump_reach[i], jump_reach[j - 1] + 1)
        max_reach = max(max_reach, i)

    return max(jump_reach)


n = int(input())
for _ in range(n):
    input()  # discard the input
    data = list(map(int, input().split()))
    print(max_jump_reach(data))
