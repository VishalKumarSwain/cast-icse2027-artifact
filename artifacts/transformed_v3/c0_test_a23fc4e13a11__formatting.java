import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import javax.swing.*;

public class CollaborativeResearchApp extends JFrame {
  private JTextArea whiteboard;
  private JTree mindMap;
  private JTextArea chatArea;
  private JTextArea messageInput;
  private ArrayList<String> versionHistory;
  private int versionCounter;

  public CollaborativeResearchApp() {
    setTitle("Collaborative Research App");
    setSize(800, 600);
    setDefaultCloseOperation(EXIT_ON_CLOSE);
    versionHistory = new ArrayList<>();
    versionCounter = 0;

    JTabbedPane tabbedPane = new JTabbedPane();

    // Whiteboard
    whiteboard = new JTextArea();
    JButton saveButton = new JButton("Save Version");
    saveButton.addActionListener(e -> saveVersion());
    JPanel whiteboardPanel = new JPanel(new BorderLayout());
    whiteboardPanel.add(new JScrollPane(whiteboard), BorderLayout.CENTER);
    whiteboardPanel.add(saveButton, BorderLayout.SOUTH);
    tabbedPane.addTab("Whiteboard", whiteboardPanel);

    // Mind Map
    DefaultMutableTreeNode root = new DefaultMutableTreeNode("Ideas");
    mindMap = new JTree(root);
    JPanel mindMapPanel = new JPanel(new BorderLayout());
    mindMapPanel.add(new JScrollPane(mindMap), BorderLayout.CENTER);
    tabbedPane.addTab("Mind Map", mindMapPanel);

    // Chat
    chatArea = new JTextArea();
    messageInput = new JTextArea(3, 20);
    JButton sendButton = new JButton("Send");
    sendButton.addActionListener(new SendMessageAction());
    JPanel chatPanel = new JPanel(new BorderLayout());
    chatPanel.add(new JScrollPane(chatArea), BorderLayout.CENTER);
    chatPanel.add(messageInput, BorderLayout.SOUTH);
    chatPanel.add(sendButton, BorderLayout.EAST);
    tabbedPane.addTab("Chat", chatPanel);

    add(tabbedPane);
    setVisible(true);
  }

  private void saveVersion() {
    versionCounter++;
    versionHistory.add("Version " + versionCounter + ": " + whiteboard.getText());
    System.out.println("Saved: " + versionHistory.get(versionCounter - 1)); // Debug Print
  }

  private class SendMessageAction implements ActionListener {
    public void actionPerformed(ActionEvent e) {
      String message = messageInput.getText().trim();
      if (!message.isEmpty()) {
        chatArea.append("You: " + message + "\n");
        messageInput.setText("");
      }
    }
  }

  public static void main(String[] args) {
    SwingUtilities.invokeLater(CollaborativeResearchApp::new);
  }
}
