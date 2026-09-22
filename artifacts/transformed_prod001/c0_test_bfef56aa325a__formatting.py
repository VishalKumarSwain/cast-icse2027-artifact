for _ in range(t):
    n = int(input())
    ar = list(map(int, input().split()))
    suma = sum(ar)
    ans = -int(2e9)
    for i in ar:
        t = i
        t += i
        t %= 2
        ans = max(ans, suma + t)
    print(ans)


"""
he sum of each side of the triangle.
If a side is obtuse, the sums of its two interior angles add up to less than 180 degrees.
Given an angle A, tw ell ABC on the circumference of a circle, ch : math :: ri = r, math :: inside triangle vertices , we can draw a line on it, and consider the points which lie on both the lines and described above as A as B.
"""
