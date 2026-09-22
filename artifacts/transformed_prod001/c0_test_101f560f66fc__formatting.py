def endPoints(self, matrix, M, N):
    # code here
    x = y = 0
    i = 0
    j = 0
    while i < M and j < N:
        if matrix[i][j] == 1:
            matrix[i][j] = 0
            temp = i
            i = j
            j = temp
            if j + 1 < N and i == 0:
                y = j + 1
            elif j == 0 and i + 1 < M:
                x = i + 1
            elif i + 1 >= M:
                y = j - 1
            elif j + 1 >= N:
                x = i - 1
            elif j - 1 >= N:
                x = i - 1
            elif i - 1 >= M:
                y = j - 1
        else:
            if j + 1 < N and x == i and i == 0:
                y = j + 1
            elif i + 1 < M and y == j and j == 0:
                x = i + 1
            elif j + 1 >= N:
                x = i - 1
            elif i + 1 >= M:
                y = j - 1
        j = y
        i = x
    return [x, y]
