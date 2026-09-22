import java.util.Scanner;

public class URI1962 {
	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		int numero,qtde;
		qtde = in.nextInt();
		
		int i = 0;
while (i < qtde) {
			numero = in.nextInt();
			if(numero < 2015) {
				System.out.println(2015 - numero + " D.C.");
			}else if(numero >= 2015) {
				System.out.println(numero - 2014 + " A.C.");
			}
		i += 1;
}
	}
}