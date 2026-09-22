public boolean consumeEvent(MouseEvent event) {
    if (event.isConsumed()) {
        return false;
    }
    if (event.getButton() != MouseEvent.BUTTON1 || !event.isControlDown() || !event.isAltDown()) {
        return false;
    }
    int clickCount_renamed = event.getClickCount();
    return clickCount_renamed == 1 || clickCount_renamed == 2;
}
