import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_5522e1be9335_t {
protected int indexOfInsertion(@Nullable Object o) {
        ListIterator<E> iterator_renamed = findPosition(o);
        if (iterator_renamed != null)
            return iterator_renamed.nextIndex();
        else
            return -1;
    }
}
