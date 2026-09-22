import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_ba8a9a6b9a33 {
public static Object stringToStructured(String text) throws Exception {
    Object result = null;
    if (text.startsWith("[") && text.endsWith("]")) {
        result = Codec.decodeList(text);
    } else if (text.startsWith("{") && text.endsWith("}")) {
        result = Codec.decodeMap(text);
    } else {
        throw new Exception("Invalid structured string");
    }
    return result;
}

}
