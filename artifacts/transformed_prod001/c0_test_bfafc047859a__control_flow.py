t = int(input())
i = 0
while i < t:
	n = int(input())
	a = list(range(1, n + 1, 2))
	b = list(range(2, n + 1, 2))
	b.reverse()
	c = a + b
	print(*c)
	i += 1
