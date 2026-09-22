import java.util.PriorityQueue;

public class Main {
  public static int maximumScore(int[] nums, int k) {
    PriorityQueue<Integer> pq = new PriorityQueue<>((a, b) -> b - a);
    for (int num : nums) {
      pq.offer(num);
    }

    int score = 0;
    while (k-- > 0) {
      int num = pq.poll();
      score += num;
      pq.offer((num + 2) / 3);
    }

    return score;
  }

  public static void main(String[] args) {
    int[] nums = {10, 10, 10, 10, 10};
    int k = 5;
    System.out.println(maximumScore(nums, k)); // Output: 50

    int[] nums2 = {1, 10, 3, 3, 3};
    int k2 = 3;
    System.out.println(maximumScore(nums2, k2)); // Output: 17
  }
}
