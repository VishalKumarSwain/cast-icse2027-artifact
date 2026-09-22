import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_ba8a9a6b9a33_t {
public static Object stringToStructured(String text) throws Exception {
    Object result_renamed = null;
    if (text.startsWith("[") && text.endsWith("]")) {
        result_renamed = Codec.decodeList(text);
    } else if (text.startsWith("{") && text.endsWith("}")) {
        result_renamed = Codec.decodeMap(text);
    } else {
        throw new Exception("Invalid structured string");
    }
    return result_renamed;
}

}
