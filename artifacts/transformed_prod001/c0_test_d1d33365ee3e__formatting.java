public class A {
  public static void main(String[] args) {
    Scanner in = new Scanner(System.in);
    int n = in.nextInt();
    int k = in.nextInt();
    if (n == 1 && k == 1) {
      System.out.print(1);
    } else {
      long result = 0;
      for (int i = 1; i <= n - k + 1; ++i) {
        result += i * (k - 1);
      }
      if (result >= 998244353) result = result % 998244353;
      System.out.print(result);
    }
  }
}
