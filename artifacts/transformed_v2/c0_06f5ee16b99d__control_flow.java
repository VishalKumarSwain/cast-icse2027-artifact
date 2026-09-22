import java.util.HashMap;
import java.util.Map;

class Solution {
    public int[] sumPrefixScores(String[] words) {
        TrieNode root = new TrieNode();
        for (String word : words) {
            insert(word, root);
        }
        int[] answer = new int[words.length];
        int i = 0;
while (i < words.length) {
            answer[i] = sumScores(words[i], root);
        i += 1;
}
        return answer;
    }

    private void insert(String word, TrieNode root) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            node = node.children.computeIfAbsent(c, k -> new TrieNode());
            node.prefixCount++;
        }
    }

    private int sumScores(String word, TrieNode root) {
        TrieNode node = root;
        int score = 0;
        for (char c : word.toCharArray()) {
            node = node.children.get(c);
            score += node.prefixCount;
        }
        return score;
    }

    private static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        int prefixCount = 0;
    }
}
