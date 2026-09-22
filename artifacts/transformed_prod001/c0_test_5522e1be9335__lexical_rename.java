protected int indexOfInsertion(@Nullable Object o) {
        ListIterator<E> iterator_renamed = findPosition(o);
        if (iterator_renamed != null)
            return iterator_renamed.nextIndex();
        else
            return -1;
    }