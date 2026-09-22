public BaseConverter findConverter(Class<?> fromType, Class<?> toType) throws ConverterNotFoundException {
    // Assuming a map of converters_renamed is available
    Map<Pair<Class<?>, Class<?>>, BaseConverter> converters_renamed = getConvertersMap();

    Pair<Class<?>, Class<?>> key = new Pair<>(fromType, toType);
    BaseConverter converter = converters_renamed.get(key);

    if (converter == null) {
        throw new ConverterNotFoundException("No converter found for types: " + fromType.getName() + " to " + toType.getName());
    }

    return converter;
}
