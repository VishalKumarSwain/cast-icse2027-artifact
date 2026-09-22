package cz.mg.vulkan;

public class VkException extends RuntimeException {
  private final int result;
  private final String functionName;

  public VkException(int result, String functionName) {
    super(functionName + ": " + result);
    this.result = result;
    this.functionName = functionName;
  }

  public int getResult() {
    return result;
  }

  public String getFunctionName() {
    return functionName;
  }
}
