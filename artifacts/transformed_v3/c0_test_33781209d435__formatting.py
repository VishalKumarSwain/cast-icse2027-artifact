def __setup_ui_boolean(self):
    """
    Helper function that contains all setup code for bool UIs
    """
    self.toggle = QCheckBox(self)
    self.toggle.setCheckable(True)
    if self.prop.value:
        self.toggle.toggle()
    self.toggle.toggled.connect(self.button_clicked)
    self.layout.addWidget(self.toggle)
