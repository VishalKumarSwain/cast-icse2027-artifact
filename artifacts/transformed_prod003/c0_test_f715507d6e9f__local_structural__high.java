public class DefaultFileLockContentionHandler implements FileLockContentionHandler, Stoppable {
    private static final Logger LOGGER = LoggerFactory.getLogger(DefaultFileLockContentionHandler.class);
    private static final int PING_DELAY = 1000;
    private final Lock lock = new ReentrantLock();

    private final Map<Long, ContendedAction> contendedActions = new HashMap<Long, ContendedAction>();
    private final Map<Long, Integer> unlocksRequestedFrom = new HashMap<Long, Integer>();
    private final Map<Long, Integer> unlocksConfirmedFrom = new HashMap<Long, Integer>();

    private final ExecutorFactory executorFactory;
    private final InetAddressFactory addressFactory;

    private FileLockCommunicator communicator;
    private ManagedExecutor fileLockRequestListener;
    private ManagedExecutor unlockActionExecutor;
    private boolean stopped;

    public DefaultFileLockContentionHandler(ExecutorFactory executorFactory, InetAddressFactory addressFactory) {
        this.executorFactory = executorFactory;
        this.addressFactory = addressFactory;
    }

    private Runnable listener() {
        return new Runnable() {
            public void run() {
                try {
                    LOGGER.debug("Starting file lock listener thread.");
                    doRun();
                } catch (Throwable t) {
                    //Logging exception here is only needed because by default Gradle does not show the stack trace
                    LOGGER.error("Problems handling incoming cache access requests.", t);
                } finally {
                    LOGGER.debug("File lock listener thread completed.");
                }
            }

            private void doRun() {
                while (true) {
                    DatagramPacket packet;
                    long lockId;
                    try {
                        packet = communicator.receive();
                        lockId = communicator.decodeLockId(packet);
                    } catch (GracefullyStoppedException e) {
                        return;
                    }

                    lock.lock();
                    ContendedAction contendedAction = contendedActions.get(lockId);
                    if (contendedAction == null) {
                        acceptConfirmationAsLockRequester(lockId, packet.getPort());
                    } else {
                        if (!contendedAction.running) {
                            startLockReleaseAsLockHolder(contendedAction);
                        }
                        communicator.confirmUnlockRequest(packet);
                    }
                    lock.unlock();
                }
            }
        };
    }

    private void startLockReleaseAsLockHolder(ContendedAction contendedAction) {
        contendedAction.running = true;
        unlockActionExecutor.execute(contendedAction.action);
    }

    private void acceptConfirmationAsLockRequester(long lockId, int port) {
        unlocksConfirmedFrom.put(lockId, port);
        LOGGER.debug("Gradle process at port {} confirmed unlock request for lock with id {}.", port, lockId);
    }

    public void start(long lockId, Runnable whenContended) {
        Runnable _extracted_0 = () -> {
        lock.lock();
        unlocksRequestedFrom.remove(lockId);
        unlocksConfirmedFrom.remove(lockId);
        };
        _extracted_0.run();
        try {
            assertNotStopped();
            if (communicator == null) {
                throw new IllegalStateException("Must initialize the handler by reserving the port first.");
            }
            if (fileLockRequestListener == null) {
                fileLockRequestListener = executorFactory.create("File lock request listener");
                fileLockRequestListener.execute(listener());
            }
            if (unlockActionExecutor == null) {
                unlockActionExecutor = executorFactory.create("File lock release action executor");
            }
            if (contendedActions.containsKey(lockId)) {
                throw new UnsupportedOperationException("Multiple contention actions for a given lock are currently not supported.");
            }
            contendedActions.put(lockId, new ContendedAction(whenContended));
        } finally {
            lock.unlock();
        }
    }

    public boolean maybePingOwner(int port, long lockId, String displayName, long timeElapsed) {
        if (Integer.valueOf(port).equals(unlocksConfirmedFrom.get(lockId))) {
            //the unlock was confirmed we are waiting
            return false;
        }
        if (Integer.valueOf(port).equals(unlocksRequestedFrom.get(lockId)) && timeElapsed < PING_DELAY) {
            //the unlock was just requested but not yet confirmed, give it some more time
            return false;
        }

        boolean pingSentSuccessfully = getCommunicator().pingOwner(port, lockId, displayName);
        if (pingSentSuccessfully) {
            Runnable _extracted_1 = () -> {
            lock.lock();
            unlocksRequestedFrom.put(lockId, port);
            lock.unlock();
            };
            _extracted_1.run();
        }
        return pingSentSuccessfully;
    }

    private void assertNotStopped() {
        if (stopped) {
            throw new IllegalStateException(
                    "Cannot start managing file contention because this handler has been closed.");
        }
    }

    public void stop(long lockId) {
        lock.lock();
        try {
            contendedActions.remove(lockId);
        } finally {
            lock.unlock();
        }
    }

    public void stop() {
        lock.lock();
        try {
            stopped = true;
            contendedActions.clear();
            if (communicator != null) {
                communicator.stop();
            }
        } finally {
            lock.unlock();
        }
        if (fileLockRequestListener != null) {
            fileLockRequestListener.stop();
        }
        if (unlockActionExecutor != null) {
            unlockActionExecutor.stop();
        }
    }

    public int reservePort() {
        return getCommunicator().getPort();
    }

    private FileLockCommunicator getCommunicator() {
        lock.lock();
        try {
            assertNotStopped();
            if (communicator == null) {
                communicator = new FileLockCommunicator(addressFactory);
            }
            return communicator;
        } finally {
            lock.unlock();
        }
    }

    private static class ContendedAction {
        private final Runnable action;
        private boolean running;

        private ContendedAction(Runnable action) {
            this.action = action;
        }
    }
}