import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_65064dce4449_t {
private boolean maybeOverwritePreviousMessage() throws IOException {
    if (useCursorControls && numLinesPreviousErasable != 0) {
      int i = 0;
while (i < numLinesPreviousErasable) {
        terminal.cr();
        terminal.cursorUp(1);
        terminal.clearLine();
      i += 1;
}
      return true;
    } else {
      return false;
    }
  }
}
