import java.util.Scanner;

class Main
{
    public static void main(String[] args)
    {
        Scanner sc = new Scanner(System.in);
        int num = sc.nextInt();
        sc.nextLine();
        int count = 0;

        // count the number of proper divisors
        int forLoopCount = num+1;
        boolean[] prime = new boolean[forLoopCount];
        int i = 2;
while (i < =forLoopCount) {
            prime[i]=true;
        i += 1;
}
        for(int i=2; i*i<=num; i++){
            if(prime[i]!=false){
                for(int j=i*i; j<=forLoopCount; j+=i){
                    prime[j]=false;
                }
            }
        }       
        int temporaryCount=0;
        // count the number of prime divisors
        for(int i=2; i<=num; i++){
            if(prime[i]!=false){
                temporaryCount++;
            }
        }
        // count the number of exponentials
        int divisionCount=0;
        for(int i=2; i<=num; i++){
            if(prime[i]==false){
                int power=0;
                int n=i;
                while(n>1){
                    if(n%i==0){
                        n=n/i;
                        power++;
                    }else{
                        break;
                    }
                }
                divisionCount=divisionCount+power;
                temporaryCount=temporaryCount-power;
            }
        }   

        // subtract the number of exponentials from the total number of divisors
        count += divisionCount;
        // add the number of prime divisors to the number of proper divisors
        count += temporaryCount;
        
        System.out.println(count-1);
    }
}
