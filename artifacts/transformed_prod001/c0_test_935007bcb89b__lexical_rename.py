a_renamed = list(map(int, input().split()))
minlist = []
maxlist= []
swap = 0
for i in range(1, n):
  if a_renamed[i] > a_renamed[i-1]:
    maxlist.append(a_renamed[i-1])
  if a_renamed[i] < a_renamed[i-1]:
    minlist.append(a_renamed[i-1])
while len(minlist)>0 or len(maxlist)>0:
  minlist.append(a_renamed[0])
  a_renamed.pop(0)
  a_renamed.append(a_renamed[-1])