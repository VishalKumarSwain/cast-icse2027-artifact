def can_transform_to_empty(grid):
    n = len(grid)
    
    for y in range(n):
        x = 0
        while x < n:
            if grid[y][x]:
                # Check if we can form a "T"-shape pattern and x, y are within bounds
                if 1 <= x <= n - 2 and y <= n - 3:
                    # Check if the "T"-shape exists
                    if (grid[y + 1][x] and grid[y + 2][x] and
                        grid[y + 1][x - 1] and grid[y + 1][x + 1]):
                        
                        # Remove the "T"-shape
                        grid[y][x] = 0
                        grid[y + 1][x] = 0
                        grid[y + 2][x] = 0
                        grid[y + 1][x - 1] = 0
                        grid[y + 1][x + 1] = 0
                    else:
                        return 'NO'
                else:
                    return 'NO'
            x += 1
    return 'YES'

def main():
    n = int(input())
    grid = [[1 if j == '.' else 0 for j in input()] for _ in range(n)]
    
    result = can_transform_to_empty(grid)
    print(result)

if __name__ == "__main__":
    main()
