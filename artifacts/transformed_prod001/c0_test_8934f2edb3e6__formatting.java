import android.animation.Animator;
import android.view.View;
import java.util.ArrayList;
import java.util.List;

public class BoundView {
  private final View boundView;
  private final int anchorOffset;
  private final List<Transformation> transformations;

  public BoundView(View view, List<Transformation> transformations) {
    this.boundView = view;
    this.anchorOffset = 0; // Default value, can be modified as needed
    this.transformations = new ArrayList<>(transformations);
  }

  public void applyTransform(float currentMoveY) {
    for (Transformation transformation : transformations) {
      transformation.apply(boundView, currentMoveY);
    }
  }

  public List<Animator> generateAnimators(float progress) {
    List<Animator> animators = new ArrayList<>();
    for (Transformation transformation : transformations) {
      Animator animator = transformation.createAnimator(boundView, anchorOffset, progress);
      if (animator != null) {
        animators.add(animator);
      }
    }
    return animators;
  }

  public interface Transformation {
    void apply(View view, float currentMoveY);

    Animator createAnimator(View view, int anchorOffset, float progress);
  }
}
