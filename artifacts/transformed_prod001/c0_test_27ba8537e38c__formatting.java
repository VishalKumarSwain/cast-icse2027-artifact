import java.applet.Applet;
import java.awt.*;
import java.awt.font.FontRenderContext;
import java.awt.font.GlyphVector;
import java.awt.image.BufferedImage;

public class AppletPaint {
  private Applet applet;
  private Graphics2D gfx;

  public AppletPaint(Applet applet, Graphics2D gfx) {
    this.applet = applet;
    this.gfx = gfx;
  }

  public void paint() {
    Graphics g = applet.getGraphics();

    // anti aliasing rendering hints
    gfx.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

    // fetch necessary resources from applet's resource manager
    BufferedImage backgroundImage = applet.getImage("background.png");
    BufferedImage buttonImage = applet.getImage("button.png");

    // get current screen type
    DisplayMode dm = applet.getScreen().getFullScreenWindow().getFullScreenWindowDisplayMode();

    // get font render context for anti-aliasing text rendering
    FontRenderContext frc =
        new FontRenderContext(
            gfx.getFontRenderContext().getDisplayList(),
            gfx.getFontRenderContext().getTransform(),
            gfx.getFontRenderContext().getAntiAliasingHint(),
            gfx.getFontRenderContext().getFractionalMetricsHint());

    // draw background image
    g.drawImage(backgroundImage, 0, 0, applet.getWidth(), applet.getHeight(), applet);

    // draw images depending on screen size
    if (dm.getWidth() <= dm.getHeight()) {
      // landscape screen
      g.drawImage(buttonImage, 50, 50, 100, 100, applet);
    } else {
      // portrait screen
      g.drawImage(buttonImage, 70, 70, 50, 50, applet);
    }

    // draw text
    String text = "Applet Title";
    GlyphVector glyphVector = applet.getFont().getGlyphVector(frc, text);
    int[] codePoints = glyphVector.getCodePoints();
    float[] subpVectors = glyphVector.getSubpixelPositions();
    float x = applet.getWidth() / 2 - glyphVector.getVisualBounds().getWidth() / 2;
    float y = applet.getHeight() / 2 + glyphVector.getVisualBounds().getHeight() / 2;
    g.setColor(Color.WHITE);
    g.drawString(text, (int) x, (int) y);
  }
}
