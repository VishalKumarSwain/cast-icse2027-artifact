import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_747312b6dc07 {
public void parseRequestHeader(byte[] lineBuf, Request req, State state) throws ParseException {
    String headerLine = new String(lineBuf);
    int colonIndex = headerLine.indexOf(':');
    if (colonIndex < 0) {
        throw new ParseException("Malformed header: " + headerLine, 0);
    }

    String headerName = headerLine.substring(0, colonIndex).trim();
    String headerValue = headerLine.substring(colonIndex + 1).trim();

    req.addHeader(headerName, headerValue);
    state.setLastHeaderName(headerName);
}

}
