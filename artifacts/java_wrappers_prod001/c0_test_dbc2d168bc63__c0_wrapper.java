import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_dbc2d168bc63 {
public static PathWatcher createSinglePathWatcher(
            Path path,
            PathChangeListener pathChangeListener,
            ExecutorService executorService,
            LifecycleListener lifecycleListener){
        Preconditions.isNotNull(path, "path");
        Preconditions.isNotNull(pathChangeListener, "pathChangeListener");
        Preconditions.isNotNull(executorService, "executorService");
        Preconditions.isNotNull(lifecycleListener, "lifecycleListener");
        PathWatcherFactory pathWatcherFactory = new PathWatcherFactory(executorService, lifecycleListener);
        return pathWatcherFactory.createNonRecursiveWatcher(path.getParent(),
                new SinglePathChangeListener(path, pathChangeListener));
    }
}
