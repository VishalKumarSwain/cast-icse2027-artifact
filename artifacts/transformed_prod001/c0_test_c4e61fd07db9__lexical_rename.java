public int longest_renamed() {
    int longest_renamed = 0;
    int prev = 0;
    while (!s.isEmpty()) {
        int current = s.poll();
        if (current > prev) {
            longest_renamed = Math.max(longest_renamed, current - prev);
            prev = current;
        }
    }
    return longest_renamed;
}
