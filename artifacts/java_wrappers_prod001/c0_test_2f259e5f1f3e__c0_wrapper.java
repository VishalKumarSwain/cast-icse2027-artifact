import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_2f259e5f1f3e {
public String generateReference(String referenceName, String jsonPtrExpr)
    {
        return CONTEXT_REFERENCE_PREFIX
            + referenceName
            + (jsonPtrExpr == null
               ? ""
               : CONTEXT_REFERENCE_SEPARATOR + jsonPtrExpr)
            + CONTEXT_REFERENCE_SUFFIX;
    }
}
