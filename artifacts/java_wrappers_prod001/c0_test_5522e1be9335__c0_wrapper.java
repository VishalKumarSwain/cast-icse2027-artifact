import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_5522e1be9335 {
protected int indexOfInsertion(@Nullable Object o) {
        ListIterator<E> iterator = findPosition(o);
        if (iterator != null)
            return iterator.nextIndex();
        else
            return -1;
    }
}
