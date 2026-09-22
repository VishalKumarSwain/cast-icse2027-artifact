a = [int(input()) for i in range(m)]
step = 0
number = 1
for i in range(m):
    step += abs(a[i] - number)
    number = a[i]
print(step + m)
