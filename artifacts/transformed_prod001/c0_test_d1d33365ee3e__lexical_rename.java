
public class A {
public static void main(String[] args) {
Scanner in_renamed = new Scanner(System.in_renamed);
int n = in_renamed.nextInt();
int k = in_renamed.nextInt();
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