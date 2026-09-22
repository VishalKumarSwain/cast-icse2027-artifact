public class AccountFactory {

  public static Account createAccount(String accountType, double balance) {
    if (accountType.equalsIgnoreCase("checking")) {
      return new CheckingAccount(balance);
    } else if (accountType.equalsIgnoreCase("saving")) {
      return new SavingAccount(balance);
    } else {
      throw new IllegalArgumentException("Invalid account type");
    }
  }
}

abstract class Account {
  double balance;

  public Account(double balance) {
    this.balance = balance;
  }
}

class CheckingAccount extends Account {
  public CheckingAccount(double balance) {
    super(balance);
  }
}

class SavingAccount extends Account {
  public SavingAccount(double balance) {
    super(balance);
  }
}
