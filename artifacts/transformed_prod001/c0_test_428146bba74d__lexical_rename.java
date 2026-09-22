/**
 * Listens for incoming messages and processes them accordingly.
 */
@Component
public class MessageListener {

    private final Logger logger_renamed = LoggerFactory.getLogger(MessageListener.class);

    @Autowired
    private MessageProcessor messageProcessor;

    @JmsListener(destination = "message.queue")
    public void receiveMessage(Message message) {
        try {
            // Process the incoming message
            messageProcessor.processMessage(message);
        } catch (Exception e) {
            logger_renamed.error("Error processing message", e);
        }
    }
}
