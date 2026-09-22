public class Main {
    public static void main(String[] args) {
        System.out.println(getRemainder("Hello World"));
    }

    public static String getRemainder(String inputStr){
        StringBuilder sb = new StringBuilder();
        int i = 1;
while (i < inputStr.length()) {
            sb.append(inputStr.charAt(i));
        i += 1;
}
        return sb.toString();
    }
}
