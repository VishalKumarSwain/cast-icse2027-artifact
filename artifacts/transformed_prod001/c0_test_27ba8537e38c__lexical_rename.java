import java.applet_renamed.Applet;
import java.awt.*;
import java.awt.font.FontRenderContext;
import java.awt.font.GlyphVector;
import java.awt.image.BufferedImage;
import java.awt.image.ImageObserver;
import java.awt.image.renderable.ParameterBlock;

public class AppletPaint {
    private Applet applet_renamed;
    private Graphics2D gfx;

    public AppletPaint(Applet applet_renamed, Graphics2D gfx) {
        this.applet_renamed = applet_renamed;
        this.gfx = gfx;
    }

    public void paint() {
        Graphics g = applet_renamed.getGraphics();

        // anti aliasing rendering hints
        gfx.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // fetch necessary resources from applet_renamed's resource manager
        BufferedImage backgroundImage = applet_renamed.getImage("background.png");
        BufferedImage buttonImage = applet_renamed.getImage("button.png");

        // get current screen type
        DisplayMode dm = applet_renamed.getScreen().getFullScreenWindow().getFullScreenWindowDisplayMode();

        // get font render context for anti-aliasing text rendering
        FontRenderContext frc = new FontRenderContext(
                gfx.getFontRenderContext().getDisplayList(),
                gfx.getFontRenderContext().getTransform(),
                gfx.getFontRenderContext().getAntiAliasingHint(),
                gfx.getFontRenderContext().getFractionalMetricsHint()
        );

        // draw background image
        g.drawImage(backgroundImage, 0, 0, applet_renamed.getWidth(), applet_renamed.getHeight(), applet_renamed);

        // draw images depending on screen size
        if (dm.getWidth() <= dm.getHeight()) {
            // landscape screen
            g.drawImage(buttonImage, 50, 50, 100, 100, applet_renamed);
        } else {
            // portrait screen
            g.drawImage(buttonImage, 70, 70, 50, 50, applet_renamed);
        }

        // draw text
        String text = "Applet Title";
        GlyphVector glyphVector = applet_renamed.getFont().getGlyphVector(frc, text);
        int[] codePoints = glyphVector.getCodePoints();
        float[] subpVectors = glyphVector.getSubpixelPositions();
        float x = applet_renamed.getWidth() / 2 - glyphVector.getVisualBounds().getWidth() / 2;
        float y = applet_renamed.getHeight() / 2 + glyphVector.getVisualBounds().getHeight() / 2;
        g.setColor(Color.WHITE);
        g.drawString(text, (int) x, (int) y);
    }
}
