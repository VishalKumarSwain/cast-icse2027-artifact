import java.lang.reflect.*;
import java.util.*;

public class CatalogReader {
  // Suppress default constructor, ensuring cloning is impossible
  private CatalogReader() {}

  // Field 'cat' of type int
  private static int getCat(Object o) {
    Method method;
    try {
      // Introspect the object to find the method that fetches 'cat' field
      method = o.getClass().getDeclaredMethod("getCat");

      // Make the method accessible, so we can invoke it directly
      method.setAccessible(true);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }

    // Invoke the method to get the value of 'cat' field
    try {
      return (Integer) method.invoke(o);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static int getCatFromRecord(Object record) {
    // TODO: invoke the method getCat and return the result
    return getCat(record);
  }
}
