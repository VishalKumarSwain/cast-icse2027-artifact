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
