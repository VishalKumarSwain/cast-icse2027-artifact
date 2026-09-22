import java.util.stream.IntStream;

public class DistanceCalculator {

  public static Integer calculateDistance(String label, String nodeA, String nodeB) {
    if (label == null || nodeA == null || nodeB == null) {
      return new IntStream().boxed().findFirst().orElse(0L);
    }

    // Simulated dataset
    // Here you would have your logic to calculate distances using the provided node labels
    // For example, let's use a mock distance method considering it as a placeholder
    long distance = mockDistanceMethod(nodeA, nodeB);

    return (int) distance;
  }

  private static long mockDistanceMethod(String nodeA, String nodeB) {
    // This method should be replaced with actual distance calculation logic
    // For now, let's assume a fixed distance for demonstration
    return 100; // Assume a fixed distance
  }

  public static void main(String[] args) {
    // Example usage
    int distance = calculateDistance("label_1", "NodeA", "NodeB");
    System.out.println("Distance: " + distance);
  }
}
