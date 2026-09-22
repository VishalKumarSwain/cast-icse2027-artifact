import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class InProcessConnectionPair {
  private final Executor executor;
  private final InProcessConnection sender;
  private final InProcessConnection receiver;

  public InProcessConnectionPair(Executor executor) {
    this.executor = executor;
    this.sender = new InProcessConnection(executor, true);
    this.receiver = new InProcessConnection(executor, false);
  }

  public InProcessConnection getSender() {
    return sender;
  }

  public InProcessConnection getReceiver() {
    return receiver;
  }

  public static class InProcessConnection {
    private final Executor executor;
    private final boolean isSender;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public InProcessConnection(Executor executor, boolean isSender) {
      this.executor = executor;
      this.isSender = isSender;
    }

    public Future<?> send(JsonNode message) {
      if (!isSender) {
        throw new IllegalStateException("This connection is not a sender");
      }
      return executor.submit(
          () -> {
            // Perform send operation
            System.out.println("Sending message: " + message);
          });
    }

    public Future<JsonNode> receive() {
      if (isSender) {
        throw new IllegalStateException("This connection is not a receiver");
      }
      return executor.submit(
          () -> {
            // Perform receive operation
            JsonNode receivedMessage = objectMapper.createObjectNode(); // Example message
            System.out.println("Received message: " + receivedMessage);
            return receivedMessage;
          });
    }
  }

  public static void main(String[] args) {
    Executor executor = Executors.newFixedThreadPool(2);
    InProcessConnectionPair pair = new InProcessConnectionPair(executor);

    Future<?> sendFuture =
        pair.getSender().send(objectMapper.createObjectNode().put("key", "value"));
    Future<JsonNode> receiveFuture = pair.getReceiver().receive();

    try {
      sendFuture.get();
      JsonNode receivedMessage = receiveFuture.get();
      System.out.println("Message received: " + receivedMessage);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
