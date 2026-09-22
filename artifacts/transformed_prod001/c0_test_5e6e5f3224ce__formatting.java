import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiButton;

public class CustomButton extends GuiButton {
  private int activeColor;
  private int inactiveColor;
  private int disabledColor;

  public CustomButton(int buttonId, int x, int y, int width, int height, String buttonText) {
    super(buttonId, x, y, width, height, buttonText);
    this.activeColor = 0xFFFFFF; // White for active
    this.inactiveColor = 0xAAAAAA; // Gray for inactive
    this.disabledColor = 0x555555; // Dark gray for disabled
  }

  @Override
  public void drawButton(Minecraft mc, int mouseX, int mouseY) {
    int color = getButtonColor();
    drawRect(x, y, x + width, y + height, color);
    drawCenteredString(
        mc.fontRenderer, displayString, x + width / 2, y + (height - 8) / 2, 0xFFFFFF);
  }

  private int getButtonColor() {
    if (!enabled) {
      return disabledColor;
    } else if (isMouseOver()) {
      return activeColor;
    } else {
      return inactiveColor;
    }
  }

  private void drawCenteredString(
      net.minecraft.client.font.TextRenderer fontRenderer, String text, int x, int y, int color) {
    int textWidth = fontRenderer.getStringWidth(text);
    fontRenderer.drawString(text, x - textWidth / 2, y, color);
  }
}
