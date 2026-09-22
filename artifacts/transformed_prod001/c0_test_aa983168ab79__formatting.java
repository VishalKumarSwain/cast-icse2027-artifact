import java.util.*;

public class Rectangle {

  static PrintWriter pw;
  static int h, w;

  public static void main(String[] args) throws IOException {
    pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));
    Scanner s = new Scanner(new BufferedReader(new InputStreamReader(System.in)));

    int t = s.nextInt();
    // int n = s.nextInt();

    while (t > 0) {
      solve(s);
      t--;
    }

    s.close();
    pw.flush();
    pw.close();
  }

  public static void solve(Scanner s) throws IOException {
    h = 121;
    w = 80;
    char screen[][] = fill_width(h, w, ' ');
    for (int x = 0; x < 121; x++) {
      for (int y = 0; y < 80; y++) {
        screen[x][y] = '#';
      }
    }

    int x1 = s.nextInt();
    int y1 = s.nextInt();
    int x2 = s.nextInt();
    int y2 = s.nextInt();
    int x3 = s.nextInt();
    int y3 = s.nextInt();

    int height = 121;
    int width = 80;

    /*
    Hasta la interseccion
    Horizontal para arriba(Dado el origen, arriba es positivo)

    */

    int r_x1 = (x1 / 16) + h / 2;
    int r_x2 = (x2 / 16) + h / 2;
    int r_x3 = (x3 / 16) + h / 2;

    int r_y1 = (-1) * (y1 / 8) + w / 2;
    ;
    int r_y2 = (-1) * (y2 / 8) + w / 2;
    int r_y3 = (-1) * (y3 / 8) + w / 2;

    System.out.println(r_x1);
    System.out.println(r_y1);

    System.out.println(r_x2);
    System.out.println(r_y2);

    System.out.println(r_x3);
    System.out.println(r_y3);

    float slope1_y = (float) ((r_y1 - r_y3)) / (r_x1 - r_x3);

    float b = (float) ((slope1_y * (-1 * r_x1)) + r_y1);
    // float slope1_x = (float) ((r_x1 - r_x3)) /(r_y1 - r_y3);

    // float dx = 0.1f;

    for (int x = 0; x < 80; x++) {
      double y = (slope1_y * x) + b;
      if (y < 121 && y > 0) {
        int y_int = ((int) (y));

        screen[y_int][x] = '#';
        // System.out.println("x:" + x + " y:" + y_int);
      }
    }

    for (int y = 0; y < 120; y++) {
      for (int x = 0; x < 79; x++) {
        // System.out.println(screen[y][x]);
        pw.print(screen[y][x]);
      }
      pw.println();
    }
    pw.flush();

    // float m = calc_slope();

  }

  public static float calc_slope(int x1, int y1, int x2, int y2) {
    float m = (float) ((y2 - y1) / (x2 - x1));
    return m;
  }

  /*public static char[][] fill_width(int h, int w, char c) {

      char screen[][] = new char[h][w];

      for (int x = 0; x < h; x++) {
          for (int y = 0; y < w; y++) {
              screen[x][y] = c;
          }
      }


      return screen;

  }*/

}
