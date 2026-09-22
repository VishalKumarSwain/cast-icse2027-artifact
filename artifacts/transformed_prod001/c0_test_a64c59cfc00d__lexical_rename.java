import java.lang.reflect.*;
import java.util.*;

public class CatalogReader{
  // Suppress default constructor, ensuring cloning is impossible
  private CatalogReader() {}

  // Field 'cat' of type int
  private static int getCat(Object o){
    Method method_renamed;
    try {
        // Introspect the object to find the method_renamed that fetches 'cat' field
        method_renamed = o.getClass().getDeclaredMethod("getCat");

        // Make the method_renamed accessible, so we can invoke it directly
        method_renamed.setAccessible(true);
    } 
    catch (Exception e){
        throw new RuntimeException(e);
    }

    // Invoke the method_renamed to get the value of 'cat' field
    try {
        return (Integer) method_renamed.invoke(o);
    } 
    catch (Exception e) {
        throw new RuntimeException(e);
    }
  }

  public static int getCatFromRecord(Object record){
    // TODO: invoke the method_renamed getCat and return the result
    return getCat(record);   
  }
}
