@OnThread(Tag.FXPlatform)
private final class ObjectBenchPanel extends TilePane {
  public ObjectBenchPanel() {
    // this.setPrefWidth(ObjectWrapper.WIDTH);
    // this.prefHeightProperty().bind()  TODO is this necessary?  HEIGHT * numrows
    JavaFXUtil.addStyleClass(this, "object-bench-panel");
  }

  /** Return the current number of rows or objects on this bench. */
  public int getNumberOfRows() {
    int objects = getChildren().size();
    if (objects == 0) {
      return 1;
    } else {
      int objectsPerRow = (int) getWidth() / ObjectWrapper.WIDTH;
      return (objects + objectsPerRow - 1) / objectsPerRow;
    }
  }

  /** Return the current number of rows or objects on this bench. */
  public int getNumberOfColumns() {
    return (int) getWidth() / ObjectWrapper.WIDTH;
  }
}
