import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_747312b6dc07_t {
public void parseRequestHeader(byte[] lineBuf, Request req, State state) throws ParseException {
    String headerLine_renamed = new String(lineBuf);
    int colonIndex = headerLine_renamed.indexOf(':');
    if (colonIndex < 0) {
        throw new ParseException("Malformed header: " + headerLine_renamed, 0);
    }

    String headerName = headerLine_renamed.substring(0, colonIndex).trim();
    String headerValue = headerLine_renamed.substring(colonIndex + 1).trim();

    req.addHeader(headerName, headerValue);
    state.setLastHeaderName(headerName);
}

}
