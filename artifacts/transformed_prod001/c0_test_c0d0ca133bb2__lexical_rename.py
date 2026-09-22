ans_renamed = []
for i in range(test_cases):
	n = int(input())
	a = list(map(int,input().split())) 
	sum = 0
	curr = a[0]	#current sum
	l = 1
	for j in range(1,n):
		if a[j] == a[j-1] + 1:  #sorted array
			curr += a[j]
			l = j + 1
		sum += l
		if sum*3 > curr*2:
			ans_renamed.append([i+1,j+1,k+1])
			continue
	if ans_renamed:
		print(*ans_renamed[0],sep=" ")
	else:
		print(-1)