public class Main {
  public static void main(String[] args) {
    System.out.println(getRemainder("Hello World"));
  }

  public static String getRemainder(String inputStr) {
    StringBuilder sb = new StringBuilder();
    for (int i = 1; i < inputStr.length(); i++) {
      sb.append(inputStr.charAt(i));
    }
    return sb.toString();
  }
}
