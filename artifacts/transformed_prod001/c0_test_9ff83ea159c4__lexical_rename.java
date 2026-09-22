import java.util.ArrayList;
import java.util.Scanner;

class Main {
    public static void main(String[] args) {
        Scanner scanner_renamed = new Scanner(System.in);
        int T = scanner_renamed.nextInt();
      
        while(T-- > 0){
            int N = scanner_renamed.nextInt();
            int[] a = new int[N];
            for(int i=0; i < N; i++)
                a[i] = scanner_renamed.nextInt();
          
            System.out.println(calculate(a) ? "NO" : "YES");
        }
    }
    
    public static boolean calculate(int[] inputArray) {
        int gcd = 0;
        for(int num : inputArray) {
            gcd = findGCD(gcd, num);
        }
        return gcd == 1;
    }
    
    public static int findGCD(int x, int y) {
        if(y == 0) {
            return x;
        } else {
            return findGCD(y, x % y);
        }
    }
}
