interface Rollback {
  void invoke();
}

class Transaction {
  private int attempts;
  private Rollback rollback;

  public Transaction(int attempts, Rollback rollback) {
    this.attempts = attempts;
    this.rollback = rollback;
  }

  public <T> T execute(Supplier<T> operation) {
    for (int i = 0; i < attempts; i++) {
      try {
        return operation.get();
      } catch (Exception e) {
        System.out.printf("Failed: %s attempts%n", i + 1);
        if (rollback != null) {
          rollback.invoke();
        }
      }
    }
    throw new RuntimeException("Exhausted attempts");
  }
}

public class Main {
  public static void main(String[] args) {
    Transaction transaction = new Transaction(3, Main::rollback);
    transaction.execute(Main::someOperation);
    transaction.execute(Main::someOtherOperation);
  }

  static void rollback() {
    // rollback operation
  }

  static String someOperation() {
    // operation here
    return "";
  }

  static String someOtherOperation() {
    // operation here
    return "";
  }
}
