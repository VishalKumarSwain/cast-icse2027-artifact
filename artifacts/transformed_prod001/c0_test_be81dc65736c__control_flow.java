import java.util.Scanner;

public class test2 {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int cnt = sc.nextInt();

        while (cnt-- > 0) {
            int n = sc.nextInt();
            char[][] arr = new char[n][n];
            int x1 = -1;
            int y1 = -1;
            int x2 = -1;
            int y2 = -1;

            int i = 0;
while (i < n) {
                String str = sc.next();
                for (int j = 0; j < n; j++) {
                    arr[i][j] = str.charAt(j);
                    if (arr[i][j] == '*') {
                        if (x1 == -1) {
                            x1 = i;
                            y1 = j;
                        } else {
                            x2 = i;
                            y2 = j;
                        }
                    }
                }
            i += 1;
}

            // Print the coordinates of the two '*' characters
            if (x1 != -1 && y1 != -1 && x2 != -1 && y2 != -1) {
                System.out.println("First '*' at: (" + x1 + ", " + y1 + ")");
                System.out.println("Second '*' at: (" + x2 + ", " + y2 + ")");
            } else {
                System.out.println("Not enough '*' characters found.");
            }
        }

        sc.close();
    }
}
