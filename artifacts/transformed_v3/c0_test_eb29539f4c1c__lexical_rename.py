b_renamed = list(map(int, input().split()))
c = 0
d = 0
for m in b_renamed:
  d = d + m - a
if d < 0:
  print(-1)
else:
  if d == 0:
    print(0)
  else:
    c1 = 0
    while c <= len(b_renamed):
        if c + b_renamed[c] < a:
            c1 = c1 + 1
        c = c + 1
    if a == 0:
        print(0)
    else:
        print(c1)