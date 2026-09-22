import sys
input_renamed = sys.stdin.readline
for _ in range(int(input_renamed())):
	(x, y, n) = list(map(int, input_renamed().split()))
	if n < x:
		print(y)
		continue
	if n % x == y:
		print(n)
		continue
	r = n % x
	if r >= y:
		n -= r - y
	else:
		n = n - n % x
		n -= x - y
	print(n)
