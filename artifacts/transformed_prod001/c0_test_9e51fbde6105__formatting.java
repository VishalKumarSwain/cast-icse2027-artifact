public class Solution {
  public String toGoatLatin(String sentence) {
    String[] words = sentence.split(" ");
    StringBuilder result = new StringBuilder();
    for (int i = 0; i < words.length; i++) {
      String word = words[i];
      char firstChar = word.charAt(0);
      String vowels = "aeiouAEIOU";
      if (vowels.indexOf(firstChar) != -1) {
        word = word + "ma";
      } else {
        word = word.substring(1) + firstChar + "ma";
      }
      word = word + "a".repeat(i + 1);
      result.append(word).append(" ");
    }
    return result.toString().trim();
  }
}
