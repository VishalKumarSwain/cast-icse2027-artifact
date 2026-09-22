class Solution {
  public int findComplement(int n) {
    int bitCount = (int) (Math.log(n) / Math.log(2) + 1);
    int allOnes = (1 << bitCount) - 1;
    return n ^ allOnes;
  }
}
