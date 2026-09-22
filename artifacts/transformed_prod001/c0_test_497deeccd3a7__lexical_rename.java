import java.util.*;
import java.util.function.IntFunction;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public static CheckpointedInputGate[] createCheckpointedMultipleInputGate(
        final AbstractInvokable toNotifyOnCheckpoint,
        final StreamConfig config,
        final SubtaskCheckpointCoordinator checkpointCoordinator,
        final TaskIOMetricGroup taskIOMetricGroup,
        final String taskName,
        final Collection<IndexedInputGate>... inputGates) {

    // Step 1: Union the input gates
    final List<InputGate> unionedInputGates_renamed = Arrays
            .stream(inputGates)
            .flatMap(Collection::stream)
            .map(InputGateUtil::createInputGate) // Assume createInputGate takes a collection
            .collect(Collectors.toList());

    // Step 2: Calculate the number of input channels per gate
    final Map<String, Integer> inputGateToNumberOfInputChannels = inputGates.flatMap(Collection::stream)
            .sorted(Comparator.comparingInt(IndexedInputGateway::getGateIndex))
            .collect(Collectors.toMap(
                    IndexedInputGateway::getGateIndex,
                    InputGateway::getNumberOfInputChannels
            ));

    // Step 3: Create the input gate to channel index offset map
    final Map<InputGate, Integer> inputGateToChannelIndexOffset = generateInputGateToChannelIndexOffsetMap(unionedInputGates_renamed);

    // Step 4: Create the checkpoint barrier handler
    final CheckpointBarrierHandler barrierHandler = createCheckpointBarrierHandler(
            config,
            inputGateToNumberOfInputChannels.values().stream(),
            checkpointCoordinator,
            taskName,
            generateChannelIndexToInputGateMap(unionedInputGates_renamed),
            inputGateToChannelIndexOffset,
            toNotifyOnCheckpoint);

    // Register checkpoint metrics
    registerCheckpointMetrics(taskIOMetricGroup, barrierHandler);

    // Register buffer received listener
    barrierHandler.getBufferReceivedListener().ifPresent(listener ->
            unionedInputGates_renamed.forEach(inputGate -> inputGate.registerBufferReceivedListener(listener))
    );

    CheckpointedInputGate[] checkpointedInputGates = IntStream.range(0, unionedInputGates_renamed.size())
            .mapToObj(i -> new CheckpointedInputGate(unionedInputGates_renamed.get(i), barrierHandler, inputGateToChannelIndexOffset.get(unionedInputGates_renamed.get(i))))
            .toArray(CheckpointedInputGate[]::new);

    return checkpointedInputGates;
}
