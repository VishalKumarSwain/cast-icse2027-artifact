public class AccountFactory {

  public static Account createAccount(String accountType, double balance_renamed) {
    if (accountType.equalsIgnoreCase("checking")) {
      return new CheckingAccount(balance_renamed);
    } else if (accountType.equalsIgnoreCase("saving")) {
      return new SavingAccount(balance_renamed);
    } else {
      throw new IllegalArgumentException("Invalid account type");
    }
  }
}

abstract class Account {
    double balance_renamed;

    public Account(double balance_renamed) {
        this.balance_renamed = balance_renamed;
    }
}

class CheckingAccount extends Account {
	public CheckingAccount(double balance_renamed) {
		super(balance_renamed);
	}
}

class SavingAccount extends Account {
	public SavingAccount(double balance_renamed) {
		super(balance_renamed);
	}
}
