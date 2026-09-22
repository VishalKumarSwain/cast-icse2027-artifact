import java.util.*;
import java.io.*;

class PilotWrapper_c0_b1252f5c3ead {
@Nullable
  private <T> Future<ValuesAndContPosition<T>> continuationBagFuture(
      StateTag contStateTag, Coder<T> elemCoder) {
    if (contStateTag.requestPosition == null) {
      return null;
    }
    return stateFuture(contStateTag, elemCoder);
  }
}
