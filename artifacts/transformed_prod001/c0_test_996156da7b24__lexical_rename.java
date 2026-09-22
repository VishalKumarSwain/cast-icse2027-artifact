package cz.mg.vulkan;

public class VkException extends RuntimeException {
    private final int result_renamed;
    private final String functionName;

    public VkException(int result_renamed, String functionName){
        super(functionName + ": " + result_renamed);
        this.result_renamed = result_renamed;
        this.functionName = functionName;
    }

    public int getResult(){
        return result_renamed;
    }

    public String getFunctionName(){
        return functionName;
    }
}