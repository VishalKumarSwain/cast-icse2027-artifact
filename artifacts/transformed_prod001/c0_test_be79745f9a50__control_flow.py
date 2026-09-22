a = [int(input()) for i in range(m)]
step = 0
number = 1
i = 0
while i < m:
    step += abs(a[i] - number)
    number = a[i]
    i += 1
print(step + m)