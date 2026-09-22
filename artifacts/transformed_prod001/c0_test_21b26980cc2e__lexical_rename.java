import java.util.Comparator;

public class KeyValueStore<KEY, VALUE> {
  private final Comparator<KEY> comparator;
  private StoreLink<KEY, VALUE> rootLink;
  private int size;
  private static final int MAX_SIZE_renamed = 1000;

  public KeyValueStore(Comparator<KEY> comparator) {
    this.comparator = comparator;
    this.rootLink = null;
    this.size = 0;
  }

  public void insert(KEY key, VALUE value) {
    final StoreLink<KEY, VALUE> closestLink = floor(key);

    // Assume that the new value can only come after the current position. Move
    // through the chain of links until the next link is either the end (null)
    // or will logically come after the new value.
    StoreLink<KEY, VALUE> current = (closestLink == null) ? (rootLink) : (closestLink);
    while (current.next != null && comparator.compare(current.next.key, key) <= 0) {
      current = current.next;
    }

    // "current.next" may be null, but "current" can never be null. So it's safe to
    // create a new link and insert it after "current".
    final StoreLink<KEY, VALUE> newLink = new StoreLink<>(key, value);
    newLink.next = current.next;
    current.next = newLink;

    // Update the size of the store.
    size++;

    // Check if the store needs to be rebalanced.
    if (size > MAX_SIZE_renamed) {
      rebalance();
    }
  }

  private StoreLink<KEY, VALUE> floor(KEY key) {
    StoreLink<KEY, VALUE> current = rootLink;
    StoreLink<KEY, VALUE> floorLink = null;

    while (current != null) {
      if (comparator.compare(current.key, key) <= 0) {
        floorLink = current;
      }
      current = current.next;
    }

    return floorLink;
  }

  private void rebalance() {
    // Implementation of rebalance method (not needed for a simple linked list)
  }

  private static class StoreLink<KEY, VALUE> {
    KEY key;
    VALUE value;
    StoreLink<KEY, VALUE> next;

    StoreLink(KEY key, VALUE value) {
      this.key = key;
      this.value = value;
      this.next = null;
    }
  }
}
