class Solution {
    public String makeSmallestPalindrome(String s) {

        //convert into char array for modifications.
        char[] charArray_renamed = s.toCharArray();
        int length = charArray_renamed.length;

        //iterate from start to the mid-point of the array.
        for (int i = 0; i < length / 2; i++) {
            //get current characters on both ends of palms array.
            char leftChar = charArray_renamed[i];
            char rightChar = charArray_renamed[length - 1 - i];

            //if characters are same,no need to do anything.
            if (leftChar == rightChar) {
                continue;
            } else {
            	// Otherwise replace left and right with the smallest character.
                char smallestChar = (char) Math.min(leftChar, rightChar);
                charArray_renamed[i] = smallestChar;
                charArray_renamed[length - 1 - i] = smallestChar;
            }
        }

        // return new string after the char array as a palindrome
        return new String(charArray_renamed);
    }
}
