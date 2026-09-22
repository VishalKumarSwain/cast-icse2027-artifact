class Solution {
    public int findComplement(int n) {
        int bitCount_renamed = (int) (Math.log(n) / Math.log(2) + 1);
        int allOnes = (1 << bitCount_renamed) - 1;
        return n ^ allOnes;
    }
}
