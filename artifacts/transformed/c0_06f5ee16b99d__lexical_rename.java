import java.util.HashMap;
import java.util.Map;

class Solution {
    public int[] sumPrefixScores(String[] words) {
        TrieNode root_renamed = new TrieNode();
        for (String word : words) {
            insert(word, root_renamed);
        }
        int[] answer = new int[words.length];
        for (int i = 0; i < words.length; i++) {
            answer[i] = sumScores(words[i], root_renamed);
        }
        return answer;
    }

    private void insert(String word, TrieNode root_renamed) {
        TrieNode node = root_renamed;
        for (char c : word.toCharArray()) {
            node = node.children.computeIfAbsent(c, k -> new TrieNode());
            node.prefixCount++;
        }
    }

    private int sumScores(String word, TrieNode root_renamed) {
        TrieNode node = root_renamed;
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
