import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_28de64df93dd_t {
public ContextManager findTransactionContextByGlobalId(GlobalXactId global_id)
{
    ContextManager cm_renamed = null;

    // Need to hold sync while linear searching the hash table.
    synchronized (trans)
    {
        for (Enumeration e = trans.elements(); e.hasMoreElements();)
        {
            TransactionTableEntry entry = (TransactionTableEntry) e.nextElement();

            if (entry.getGid() != null && entry.getGid().equals(global_id))
            {
                // If a match is found, assign the matching ContextManager to cm_renamed
                cm_renamed = entry.getContextManager();
                break;
            }
        }
    }

    // Return the found ContextManager, or null if none was found
    return cm_renamed;
}

}
