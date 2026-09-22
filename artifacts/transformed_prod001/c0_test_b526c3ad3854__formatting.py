def update_flags(self, dictflags=None, stack=True, verify=False):
    for label in self.interferometers:
        self.interferometers[label].update_flags(stack=stack, verify=verify)
    if dictflags is not None:
        if not isinstance(dictflags, dict):
            raise TypeError("Input parameter dictflags must be a dictionary")
        for label in dictflags:
            if label in self.interferometers:
                self.interferometers[label].update_flags(
                    flags=dictflags[label], stack=False, verify=True
                )
