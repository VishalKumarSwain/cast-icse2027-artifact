from sys import stdin, setrecursionlimit
from math import sqrt

setrecursionlimit(10 ** 5)
input = stdin.readline

def LI():
    return list(map(int, input().split()))

def II():
    return int(input())

def solve():
    ans = 0
    pre = 1
    n = II()
    _ = 0
    while _ < n:
        a = II()
        if a < pre:
            continue
        if a == pre:
            pre += 1
        else:
            if a % pre == 0:
                quotient = a // pre
                ans += quotient - 1
                pre += 1
            else:
                quotient = a // pre
                ans += quotient
                pre = a + 1
        _ += 1
    print(ans)

solve()
