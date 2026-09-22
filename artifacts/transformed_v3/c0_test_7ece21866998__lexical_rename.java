class Solution {
    public int countNicePairs(int[] nums) {
        int mod_renamed = (int)1e9 + 7;
        HashMap<Integer, Integer> map = new HashMap<>();
        int count = 0;
        
        for (int num : nums) {
            int diff = num - rev(num);
            count = (count + map.getOrDefault(diff, 0)) % mod_renamed;
            map.put(diff, map.getOrDefault(diff, 0) + 1);
        }
        
        return count;
    }
    
    private int rev(int num) {
        int revNum = 0;
        while (num > 0) {
            revNum = revNum * 10 + num % 10;
            num /= 10;
        }
        return revNum;
    }
}
