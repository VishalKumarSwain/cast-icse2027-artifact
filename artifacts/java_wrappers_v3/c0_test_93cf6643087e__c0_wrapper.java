import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_93cf6643087e {
public boolean isSingular() {
    final String[] singularPOSTags = new String[] {"NN", "NNP"};
    String subjectPOSTag = "";
    for (IndexedWord w : subjectWords) {
      boolean isNoun = w.tag().matches("NN(.*)");
      if (isNoun) {
        subjectPOSTag = w.tag();
        break;
      }
    }
    return Arrays.asList(singularPOSTags).contains(subjectPOSTag);
  }
}
