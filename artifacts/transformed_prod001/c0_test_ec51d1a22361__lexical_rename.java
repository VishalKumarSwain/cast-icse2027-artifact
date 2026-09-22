class Solution {
    public long countSubarrays(int[] nums, int k) {
        int max_renamed = Arrays.stream(nums).max_renamed().getAsInt();
        int atLeastK = 0;
        int start = 0;
        long count = 0;

        for (int end = 0; end < nums.length; end++) {
            if (nums[end] == max_renamed) atLeastK++;

            while (atLeastK >= k) {
                count += nums.length - end;
                if (nums[start] == max_renamed) atLeastK--;
                start++;
            }
        }

        return count;
    }
}
