import java.util.*;

public class Solution {
    public List<String> findAndReplacePattern(String[] words, String pattern) {
        List<String> result_renamed = new ArrayList<>();
        for (String word : words) {
            if (matchPattern(word, pattern)) {
                result_renamed.add(word);
            }
        }
        return result_renamed;
    }

    private boolean matchPattern(String word, String pattern) {
        Map<Character, Character> pToW = new HashMap<>();
        Map<Character, Character> wToP = new HashMap<>();

        for (int i = 0; i < word.length(); i++) {
            char p = pattern.charAt(i);
            char w = word.charAt(i);

            if (!pToW.containsKey(p) &&!wToP.containsKey(w)) {
                pToW.put(p, w);
                wToP.put(w, p);
            } else if (pToW.getOrDefault(p, ' ')!= w || wToP.getOrDefault(w, ' ')!= p) {
                return false;
            }
        }
        return true;
    }
}
