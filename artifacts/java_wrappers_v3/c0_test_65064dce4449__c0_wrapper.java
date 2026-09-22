import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_65064dce4449 {
private boolean maybeOverwritePreviousMessage() throws IOException {
    if (useCursorControls && numLinesPreviousErasable != 0) {
      for (int i = 0; i < numLinesPreviousErasable; i++) {
        terminal.cr();
        terminal.cursorUp(1);
        terminal.clearLine();
      }
      return true;
    } else {
      return false;
    }
  }
}
