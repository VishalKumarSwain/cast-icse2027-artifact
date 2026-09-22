import java.util.Arrays;

public class Main {

  public static void main(String[] args) throws IOException {
    FastReader reader = new FastReader();
    int T = reader.readInt();
    int[] result = new int[T];
    for (int t = 0; t < T; t++) {
      int n = reader.readInt();
      int[] array = new int[n];
      for (int i = 0; i < n; i++) {
        array[i] = reader.readInt();
      }
      result[t] = solve(array, n);
    }

    for (int t = 0; t < T; t++) {
      System.out.println(result[t]);
    }
  }

  public static int solve(int[] array, int n) {
    Arrays.sort(array);
    int max = -1;
    int left = -array[0];
    int right = array[n - 1];

    for (int i = 1; i <= right / 2; i++) {
      int tmp1 = count(array, n, i);
      int tmp2 = count(array, n, i - 1);
      if (tmp1 > tmp2) {
        max = i;
        left = tmp2 - tmp1;
        break;
      }
    }
    for (int i = 1; i <= right / 2; i++) {
      int tmp1 = count(array, n, i);
      int tmp2 = count(array, n, i + 1);
      if (tmp1 >= left + 1 && tmp1 - left == tmp2) {
        return i;
      }
    }
    return max;
  }

  public static int count(int[] array, int n, int k) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
      sum += (array[i] + k) / 2 * 2;
    }
    return sum / k;
  }
}

class FastReader {
  BufferedReader br;
  StringTokenizer st;

  public FastReader() {
    br = new BufferedReader(new InputStreamReader(System.in));
  }

  public String next() {
    while (st == null || !st.hasMoreElements()) {
      try {
        st = new StringTokenizer(br.readLine());
      } catch (IOException e) {
        e.printStackTrace();
      }
    }
    return st.nextToken();
  }

  public int readInt() {
    return Integer.parseInt(next());
  }
}
