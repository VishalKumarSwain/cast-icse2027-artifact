/** Listens for incoming messages and processes them accordingly. */
@Component
public class MessageListener {

  private final Logger logger = LoggerFactory.getLogger(MessageListener.class);

  @Autowired private MessageProcessor messageProcessor;

  @JmsListener(destination = "message.queue")
  public void receiveMessage(Message message) {
    try {
      // Process the incoming message
      messageProcessor.processMessage(message);
    } catch (Exception e) {
      logger.error("Error processing message", e);
    }
  }
}
