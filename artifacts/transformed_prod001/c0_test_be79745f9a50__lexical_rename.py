a_renamed = [int(input()) for i in range(m)]
step = 0
number = 1
for i in range(m):
    step += abs(a_renamed[i] - number)
    number = a_renamed[i]
print(step + m)