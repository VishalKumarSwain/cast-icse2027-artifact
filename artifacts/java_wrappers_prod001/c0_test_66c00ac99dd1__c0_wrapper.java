import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_66c00ac99dd1 {
@Override
protected void releaseNativeHandle() {
    // It is perfectly acceptable for this to have never created a native resource
    if (!isNull()) {
        tlsContextOptionsDestroy(getNativeHandle());
        setNativeHandle(null); // Ensure the handle is set to null after destruction
    }
}

}
