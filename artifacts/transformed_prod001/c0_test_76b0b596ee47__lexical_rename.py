def max_balance(n, blue_cards, m, red_cards):
    blue_card_counts_renamed = {}
    red_card_counts = {}

    # Count occurrences of strings on blue and red cards
    for card in blue_cards:
        if card in blue_card_counts_renamed:
            blue_card_counts_renamed[card] += 1
        else:
            blue_card_counts_renamed[card] = 1

    for card in red_cards:
        if card in red_card_counts:
            red_card_counts[card] += 1
        else:
            red_card_counts[card] = 1

    max_earnings = 0

    # Iterate over all unique strings
    for card in set(blue_cards + red_cards):
        earnings = blue_card_counts_renamed.get(card, 0) - red_card_counts.get(card, 0)
        # Update max earnings
        max_earnings = max(max_earnings, earnings)

    return max_earnings


n = int(input())

blue_cards = [input() for _ in range(n)]

m = int(input())

red_cards = [input() for _ in range(m)]

max_earnings = max_balance(n, blue_cards, m, red_cards)

# Print max possible price
print(max_earnings)
