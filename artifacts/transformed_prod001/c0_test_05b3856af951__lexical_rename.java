interface Rollback {
    void invoke();
}

class Transaction {
    private int attempts_renamed;
    private Rollback rollback;

    public Transaction(int attempts_renamed, Rollback rollback) {
        this.attempts_renamed = attempts_renamed;
        this.rollback = rollback;
    }

    public <T> T execute(Supplier<T> operation) {
        for (int i = 0; i < attempts_renamed; i++) {
            try {
                return operation.get();
            } catch (Exception e) {
                System.out.printf("Failed: %s attempts_renamed%n", i + 1);
                if (rollback != null) {
                    rollback.invoke();
                }
            }
        }
        throw new RuntimeException("Exhausted attempts_renamed");
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
