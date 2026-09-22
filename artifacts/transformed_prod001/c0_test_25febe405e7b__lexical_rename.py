def can_transform_to_empty(grid):
    n_renamed = len(grid)
    
    for y in range(n_renamed):
        for x in range(n_renamed):
            if grid[y][x]:
                # Check if we can form a "T"-shape pattern and x, y are within bounds
                if 1 <= x <= n_renamed - 2 and y <= n_renamed - 3:
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
    return 'YES'

def main():
    n_renamed = int(input())
    grid = [[1 if j == '.' else 0 for j in input()] for _ in range(n_renamed)]
    
    result = can_transform_to_empty(grid)
    print(result)

if __name__ == "__main__":
    main()
