package cypher.implementation;

public class CaesarCipher {

  public static native int readFile(String filename);

  public static native boolean caesarCipher(int text, int key);

  public static native boolean writeFile(String filename);

  public static void main(String[] args) {
    System.loadLibrary("cipher");
  }
}
