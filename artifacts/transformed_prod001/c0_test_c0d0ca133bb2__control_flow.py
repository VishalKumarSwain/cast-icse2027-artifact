ans = []
for i in range(test_cases):
	n = int(input())
	a = list(map(int,input().split())) 
	sum = 0
	curr = a[0]	#current sum
	l = 1
	j = 1
	while j < n:
		if a[j] == a[j-1] + 1:  #sorted array
			curr += a[j]
			l = j + 1
		sum += l
		if sum*3 > curr*2:
			ans.append([i+1,j+1,k+1])
			continue
		j += 1
	if ans:
		print(*ans[0],sep=" ")
	else:
		print(-1)