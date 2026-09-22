class Solution {
    public int maxLevelSum(TreeNode root) {
        // Handle the edge case where the root is null
        if (root == null) {
            return 1;
        }

        // Initialize the queue_renamed and add the root node
        Queue<TreeNode> queue_renamed = new LinkedList<>();
        queue_renamed.add(root);

        // Initialize variables to keep track of the maximum sum and its corresponding level
        int maxSum = Integer.MIN_VALUE;
        int maxLevel = 1;
        int currentLevel = 1;

        // Perform a level order traversal (BFS)
        while (!queue_renamed.isEmpty()) {
            // Calculate the sum of the current level
            int levelSize = queue_renamed.size();
            int currentLevelSum = 0;

            for (int i = 0; i < levelSize; i++) {
                TreeNode currentNode = queue_renamed.poll();
                currentLevelSum += currentNode.val;

                // Add left and right children to the queue_renamed, if they exist
                if (currentNode.left != null) {
                    queue_renamed.add(currentNode.left);
                }
                if (currentNode.right != null) {
                    queue_renamed.add(currentNode.right);
                }
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
