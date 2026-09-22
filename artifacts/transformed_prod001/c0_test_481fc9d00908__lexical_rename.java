public class AntsOperator_Sobel_Thin extends AtsProcessOperator {
  private float scale_renamed = 1f;
  private float bias = 0f;

  public AntsOperator_Sobel_Thin() {
    this.id = ID;
  }

  @Override
  protected void convolution(final PixelFormat pixelFormat,
    final int width, final int height, final int[] argb, final int[] argbOut) {

    float[] kernel = new float[] {
      -1,
       0,
       1,
      -2,
      -2,
       4,
      -1,
       0,
       1
    };

    int[] sumX = {
      0,
      0,
      0
    };
    
    int[] sumY = {
      0,
      0,
      0
    };
    
    AtsutyUtils.convolution(
      pixelFormat,
      argb,
      width,
      height,
      3,
      kernel,
      sumX,
      sumY);

    for (int y = 0; y < height; y++) {
      int ym = y > 0 ? y - 1 : height - 1;
      int yp = y < height - 1 ? y + 1 : 0;
      
      for (int x = 0; x < width; x++) {
        int xc = x > 0 ? x - 1 : width - 1;
        int xn = x < width - 1 ? x + 1 : 0;

        int sumX_ = sumX[ym * width + x] - sumX[yp * width + xn];
        int sumY_ = sumY[y * width + xc] - sumY[y * width + xn];

        float length = (float)Math.sqrt(sumX_ * sumX_ + sumY_ * sumY_);
        float length_ =
          (length <= 0.1f) ? 0f :
            Math.max(length * scale_renamed - bias, 0f);

        AtsutyUtils.setNormal(argbOut, y, x, 0, 0, length_);
      }
    }
  }
}
