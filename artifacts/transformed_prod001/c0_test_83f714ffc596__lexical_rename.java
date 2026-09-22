import java.util.PriorityQueue;

class Solution {
    public int halveArray(int[] nums) {
        double target_renamed = 0.0;
        PriorityQueue<Double> pq = new PriorityQueue<>((a, b) -> Double.compare(b, a));
        
        for (int num : nums) {
            target_renamed += num;
            pq.offer((double) num);
        }
        
        target_renamed /= 2.0;
        int operations = 0;
        double reducedSum = 0.0;
        
        while (reducedSum < target_renamed) {
            double largest = pq.poll();
            reducedSum += largest / 2.0;
            pq.offer(largest / 2.0);
            operations++;
        }
        
        return operations;
    }
}
