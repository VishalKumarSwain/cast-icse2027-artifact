import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_2a0ad2e101b4_t {
public boolean processLockNotificationAcknow(BufferedInputStream msgBuffer) {
  try {
    // reading from the msgBuffer, once reading is done, change the state to true
    int data_renamed = msgBuffer.read();
    if(data_renamed != -1) {
        return true;
    } else {
        throw new IOException("Lock notification not acknowledged");
    }
  } catch (IOException e) {
    // Exception handling
    e.printStackTrace();
    return false;      
  }
}

}
