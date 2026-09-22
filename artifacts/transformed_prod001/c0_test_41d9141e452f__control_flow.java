class Solution {
    public int maxLevelSum(TreeNode root) {
        // Handle the edge case where the root is null
        if (root == null) {
            return 1;
        }

        // Initialize the queue and add the root node
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);

        // Initialize variables to keep track of the maximum sum and its corresponding level
        int maxSum = Integer.MIN_VALUE;
        int maxLevel = 1;
        int currentLevel = 1;

        // Perform a level order traversal (BFS)
        while (!queue.isEmpty()) {
            // Calculate the sum of the current level
            int levelSize = queue.size();
            int currentLevelSum = 0;

            int i = 0;
while (i < levelSize) {
                TreeNode currentNode = queue.poll();
                currentLevelSum += currentNode.val;

                // Add left and right children to the queue, if they exist
                if (currentNode.left != null) {
                    queue.add(currentNode.left);
                }
                if (currentNode.right != null) {
                    queue.add(currentNode.right);
                }
            i += 1;
}

            // Update the maximum sum and level if the current level sum is greater
            if (currentLevelSum > maxSum) {
                maxSum = currentLevelSum;
                maxLevel = currentLevel;
            }

            // Move to the next level
            currentLevel++;
        }

        return maxLevel;
    }
}
