def attack(self, mode_renamed=None):
        """Perform the attack."""
        if not mode_renamed:
            mode_renamed = self.mode_renamed
        self.start = time.time()
        # Create adversarial image from original image.
        self.adv = self.cem_att.attack(self.img, self.target, mode_renamed).detach()
        delta = self.img - self.adv

        # Calculate probability classes for adversarial and delta image.
        self.adv_pred, self.adv_label, self.adv_str = self.prediction(self.adv)
        self.delta_pred, self.delta_label, self.delta_str = \
            self.prediction(delta)

        # Perform appropriate scaling.
        self.delta = abs(delta) - 0.5
        self.end = time.time()