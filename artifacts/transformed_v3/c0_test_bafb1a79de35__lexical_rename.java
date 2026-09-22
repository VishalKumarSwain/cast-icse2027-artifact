public class Main {
    public static void main(String[] args) {
        System.out.println(getRemainder("Hello World"));
    }

    public static String getRemainder(String inputStr){
        StringBuilder sb_renamed = new StringBuilder();
        for (int i = 1; i < inputStr.length(); i++) {
            sb_renamed.append(inputStr.charAt(i));
        }
        return sb_renamed.toString();
    }
}
