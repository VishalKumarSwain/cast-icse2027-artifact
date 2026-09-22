import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

class Publication {
  String title;
  String author;
  String category;

  Publication(String title, String author, String category) {
    this.title = title;
    this.author = author;
    this.category = category;
  }
}

class User {
  String username;
  String password;

  User(String username, String password) {
    this.username = username;
    this.password = password;
  }
}

class CMS {
  private List<Publication> publications = new ArrayList<>();
  private List<User> users = new ArrayList<>();
  private User loggedInUser;

  void register(String username, String password) {
    users.add(new User(username, password));
  }

  boolean login(String username, String password) {
    for (User user : users) {
      if (user.username.equals(username) && user.password.equals(password)) {
        loggedInUser = user;
        return true;
      }
    }
    return false;
  }

  void addPublication(String title, String author, String category) {
    publications.add(new Publication(title, author, category));
  }

  List<Publication> searchPublications(String query) {
    List<Publication> results = new ArrayList<>();
    for (Publication pub : publications) {
      if (pub.title.contains(query) || pub.author.contains(query) || pub.category.contains(query)) {
        results.add(pub);
      }
    }
    return results;
  }

  void uploadFile(String filePath) {
    try {
      // Simulated file upload logic
      // Typically, file I/O handling would be added here
      System.out.println("File uploaded from: " + filePath);
    } catch (Exception e) {
      System.out.println("Error during upload: " + e.getMessage());
    }
  }

  public static void main(String[] args) {
    CMS cms = new CMS();
    Scanner scanner = new Scanner(System.in);

    System.out.println("Register a new user: ");
    System.out.print("Username: ");
    String username = scanner.nextLine();
    System.out.print("Password: ");
    String password = scanner.nextLine();
    cms.register(username, password);

    System.out.println("Log in user: ");
    System.out.print("Username: ");
    username = scanner.nextLine();
    System.out.print("Password: ");
    password = scanner.nextLine();
    if (cms.login(username, password)) {
      System.out.println("Login successful.");
      cms.addPublication("Research on AI", username, "Artificial Intelligence");
      cms.uploadFile("paper.pdf");
      List<Publication> searchResults = cms.searchPublications("AI");
      for (Publication pub : searchResults) {
        System.out.println("Found: " + pub.title + " by " + pub.author);
      }
    } else {
      System.out.println("Invalid login.");
    }

    scanner.close();
  }
}
