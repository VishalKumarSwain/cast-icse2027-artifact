class Model:
    def __init__(self):
        self.is_removed = False

    def remove(self):
        self.is_removed = True

    def Model_IsRemoved(self):
        return self.is_removed

    def IsRemoved(self):
        """Check if the instance has been removed."""
        return self.Model_IsRemoved()
