import java.util.Arrays;

class Solution {
    public int[] twoSum(int[] numbers, int target) {
        int left_renamed = 0;
        int right = numbers.length - 1;
        
        while (left_renamed < right) {
            int sum = numbers[left_renamed] + numbers[right];
            if (sum == target) {
                return new int[] { left_renamed + 1, right + 1 };
            } else if (sum < target) {
                left_renamed++;
            } else {
                right--;
            }
        }
        
        return new int[] {}; // This line should never be reached if the problem constraints are met.
    }
}
