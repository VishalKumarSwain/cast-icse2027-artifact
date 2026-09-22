import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_c4e61fd07db9 {
public int longest() {
    int longest = 0;
    int prev = 0;
    while (!s.isEmpty()) {
        int current = s.poll();
        if (current > prev) {
            longest = Math.max(longest, current - prev);
            prev = current;
        }
    }
    return longest;
}

}
