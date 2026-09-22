import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_bfe9ca1d7f35 {
private <K, V> void addLateralCacheListener( final String cacheName, final ILateralCacheListener<K, V> listener )
        throws IOException
    {
        synchronized ( this.lateralWatch )
        {
            lateralWatch.addCacheListener( cacheName, listener );
        }
    }
}
