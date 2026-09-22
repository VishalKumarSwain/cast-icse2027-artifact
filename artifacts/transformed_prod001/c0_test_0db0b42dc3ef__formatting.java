import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;

public class PerformanceMonitor {
  private long startTime;
  private long endTime;
  private int successCount;
  private int errorCount;
  private String logFilePath;

  public PerformanceMonitor(String logFilePath) {
    this.logFilePath = logFilePath;
    this.successCount = 0;
    this.errorCount = 0;
  }

  public void startJob() {
    startTime = System.currentTimeMillis();
  }

  public void endJob(boolean success) {
    endTime = System.currentTimeMillis();
    if (success) {
      successCount++;
    } else {
      errorCount++;
    }
    logPerformance(success);
  }

  private void logPerformance(boolean success) {
    try (BufferedWriter writer = new BufferedWriter(new FileWriter(logFilePath, true))) {
      String status = success ? "SUCCESS" : "ERROR";
      long executionTime = endTime - startTime;
      String logEntry =
          String.format(
              "%s | Job Status: %s | Execution Time: %d ms | Total Successful: %d | Total Errors:"
                  + " %d%n",
              LocalDateTime.now(), status, executionTime, successCount, errorCount);
      writer.write(logEntry);
    } catch (IOException e) {
      e.printStackTrace(); // consider logging the error in a more robust way in production
    }
  }

  public static void main(String[] args) {
    PerformanceMonitor monitor = new PerformanceMonitor("performance_log.txt");

    monitor.startJob();
    try {
      // Simulate a data processing job
      Thread.sleep(1000); // Simulated workload
      monitor.endJob(true);
    } catch (InterruptedException e) {
      monitor.endJob(false);
    }
  }
}
