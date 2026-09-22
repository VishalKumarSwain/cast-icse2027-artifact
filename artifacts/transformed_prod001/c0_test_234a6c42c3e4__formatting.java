public class MixinTypeListModel extends ListModel<NodeType> {
  private static final long serialVersionUID = 1L;

  public MixinTypeListModel() {
    populate();
  }

  @Override
  protected String getValue(final NodeType model) {
    return model.getName();
  }

  private void populate() {
    final TreeMap<String, NodeType> map = new TreeMap<String, NodeType>();

    try {
      for (final NodeTypeIterator iter =
              getController().getWorkspace().getNodeTypeManager().getMixinNodeTypes();
          iter.hasNext(); ) {
        final NodeType type = iter.nextNodeType();
        map.put(type.getName(), type);
      }
    } catch (Throwable t) {
      getApplication().processFatalException(t);
    }

    for (final NodeType type : map.values()) {
      add(type);
    }
  }
}
