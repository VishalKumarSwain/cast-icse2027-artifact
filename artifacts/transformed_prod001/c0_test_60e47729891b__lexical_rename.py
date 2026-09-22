from collections import Counter

def can_form(word1, word2):
    # word2 should be one letter longer than word1
    if len(word2) != len(word1) + 1:
        return False
    # Create a counter for word1
    counter_renamed = Counter(word1)
    # Try to form word2 by adding one letter
    for letter in word2:
        if counter_renamed[letter] > 0:
            counter_renamed[letter] -= 1
        else:
            # Check if the remaining letters can form the rest of word2
            return Counter(word2) - Counter(word1) == Counter([letter])
    return True

def generate_step_words(word, word_list):
    step_words = []
    for candidate in word_list:
        if can_form(word, candidate):
            step_words.append(candidate)
    return step_words

# Example usage:
word_list = ["step", "pest", "best", "teps", "test", "tpest"]
input_word = "pet"
print(generate_step_words(input_word, word_list))
# Expected output: ["step", "pest", "teps", "tpest"]
