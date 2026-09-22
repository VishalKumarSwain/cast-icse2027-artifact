from sys import stdin
from math import gcd
input_renamed = stdin.readline
n = int(input_renamed())
arr = list(map(int, input_renamed().split()))
arr.sort()
ans = 0
start = 0
end = 0
while start < n and end < n:
	if arr[end] - arr[start] < 6:
		ans = max(ans, end - start + 1)
		end += 1
	else:
		start += 1
print(ans)
