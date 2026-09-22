class Solution {
  public long countSubarrays(int[] nums, int k) {
    int max = Arrays.stream(nums).max().getAsInt();
    int atLeastK = 0;
    int start = 0;
    long count = 0;

    for (int end = 0; end < nums.length; end++) {
      if (nums[end] == max) atLeastK++;

      while (atLeastK >= k) {
        count += nums.length - end;
        if (nums[start] == max) atLeastK--;
        start++;
      }
    }

    return count;
  }
}
