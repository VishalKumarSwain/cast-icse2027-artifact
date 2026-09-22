class Solution {
  public boolean checkXMatrix(int[][] grid) {
    int n = grid.length;

    // Check each element in the matrix
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if ((i == j || i + j == n - 1)) { // Check diagonal elements
          if (grid[i][j] == 0) return false; // Not on a diagonal; it must be zero
        } else { // Not on a diagonal
          if (grid[i][j] != 0) return false; // On a non-diagonal; it must be non-zero
        }
      }
    }

    return true; // All elements checked and conditions met
  }
}
