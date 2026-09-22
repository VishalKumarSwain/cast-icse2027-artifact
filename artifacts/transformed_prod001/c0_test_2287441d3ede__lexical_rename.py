import sys
input_renamed = sys.stdin.readline
import collections

def make_divisors(n):
	divisors = []
	for i in range(1, int(n ** 0.5) + 1):
		if n % i == 0:
			divisors.append(i)
			if i != n // i:
				divisors.append(n // i)
	divisors.sort()
	return divisors

def main():
	(N, M, K) = [int(x) for x in input_renamed().split()]
	A = [int(x) for x in input_renamed().split()]
	B = [int(x) for x in input_renamed().split()]
	divs = make_divisors(K)
	ac = collections.Counter()
	acont = 0
	for a in A:
		if a == 0:
			for d in divs:
				if acont >= d:
					ac[d] += acont - d + 1
				else:
					break
			acont = 0
		else:
			acont += 1
	else:
		for d in divs:
			if acont >= d:
				ac[d] += acont - d + 1
			else:
				break
	bcont = 0
	bc = collections.Counter()
	for b in B:
		if b == 0:
			for d in divs:
				if bcont >= d:
					bc[d] += bcont - d + 1
				else:
					break
			bcont = 0
		else:
			bcont += 1
	else:
		for d in divs:
			if bcont >= d:
				bc[d] += bcont - d + 1
			else:
				break
	ans = 0
	for d in divs:
		ad = K // d
		ans += ac[d] * bc[ad]
	print(ans)
main()
