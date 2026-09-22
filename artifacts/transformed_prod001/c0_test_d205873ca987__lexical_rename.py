def update_menu_bar(self):
    # Define the new and cleanup methods based on the current format
    method_new_renamed = f'_create_{self.format}_tools_and_menu_items'
    method_cleanup = f'_cleanup_{self.menu_bar_format}_tools_and_menu_items'

    # Setting the format to 'cwo' is redundant if it does not get changed later,
    # but if it has any significance, we keep it as such.
    self.menu_bar_format = 'cwo'

    # Check if the new method exists and update the menu bar
    if self.menu_bar_format is None or not hasattr(self, method_new_renamed):
        self._update_menu_bar_to_format(self.format, method_cleanup)
    else:
        if not pyNastran.is_pynastrangui_exe:  # pragma: no cover
            print(f'need to add {method_new_renamed!r}')

        # Check if the format has changed and if the cleanup method exists
        if self.menu_bar_format != self.format and hasattr(self, method_cleanup):
            self.menu_bar_format = None
            getattr(self, method_cleanup)()

        # If the new method exists, update the menu bar
        if hasattr(self, method_new_renamed):
            self._update_menu_bar_to_format(self.format, method_new_renamed)

# If there is no new format, ensure the format is updated properly
