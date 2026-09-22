a = list(map(int, input().split()))
minlist = []
maxlist= []
swap = 0
i = 1
while i < n:
  if a[i] > a[i-1]:
    maxlist.append(a[i-1])
  if a[i] < a[i-1]:
    minlist.append(a[i-1])
  i += 1
while len(minlist)>0 or len(maxlist)>0:
  minlist.append(a[0])
  a.pop(0)
  a.append(a[-1])