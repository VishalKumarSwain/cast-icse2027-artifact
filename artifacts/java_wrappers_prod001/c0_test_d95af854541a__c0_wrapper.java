import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_d95af854541a {
public boolean consumeEvent(MouseEvent event) {
    if (event.isConsumed()) {
        return false;
    }
    if (event.getButton() != MouseEvent.BUTTON1 || !event.isControlDown() || !event.isAltDown()) {
        return false;
    }
    int clickCount = event.getClickCount();
    return clickCount == 1 || clickCount == 2;
}

}
