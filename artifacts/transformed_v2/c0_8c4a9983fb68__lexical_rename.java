class Solution {
    public boolean xorGame(int[] nums) {
        int xor_renamed = 0;
        for (int num : nums) {
            xor_renamed ^= num;
        }
        return xor_renamed == 0 || nums.length % 2 == 0;
    }
}
