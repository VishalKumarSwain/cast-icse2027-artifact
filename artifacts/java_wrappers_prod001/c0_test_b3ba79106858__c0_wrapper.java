import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_b3ba79106858 {
public BaseConverter findConverter(Class<?> fromType, Class<?> toType) throws ConverterNotFoundException {
    // Assuming a map of converters is available
    Map<Pair<Class<?>, Class<?>>, BaseConverter> converters = getConvertersMap();

    Pair<Class<?>, Class<?>> key = new Pair<>(fromType, toType);
    BaseConverter converter = converters.get(key);

    if (converter == null) {
        throw new ConverterNotFoundException("No converter found for types: " + fromType.getName() + " to " + toType.getName());
    }

    return converter;
}

}
