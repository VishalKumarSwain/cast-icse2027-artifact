public static PathWatcher createSinglePathWatcher(
            Path path,
            PathChangeListener pathChangeListener,
            ExecutorService executorService,
            LifecycleListener lifecycleListener){
        Runnable _extracted_0 = () -> {
        Preconditions.isNotNull(path, "path");
        Preconditions.isNotNull(pathChangeListener, "pathChangeListener");
        Preconditions.isNotNull(executorService, "executorService");
        Preconditions.isNotNull(lifecycleListener, "lifecycleListener");
        };
        _extracted_0.run();
        PathWatcherFactory pathWatcherFactory = new PathWatcherFactory(executorService, lifecycleListener);
        return pathWatcherFactory.createNonRecursiveWatcher(path.getParent(),
                new SinglePathChangeListener(path, pathChangeListener));
    }