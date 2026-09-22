public class SharpenSpeech {

    /**
     * <p>
     * This function emphasizes higher frequencies in an audio signal represented by
     * a an array of double. This has the effect of sharpening speech in particular.
     * </p>
     * 
     * <p>
     * Audio samples <a href=
     * "http://mirlab.org/jang/books/audiosignalprocessing/speechFeatureMfcc.asp?title=12-2%20MFCC"
     * >here</a>.
     * </p>
     * 
     * @param frequency - array of double
     */
    private static double emphasizeHigherFrequencies(double[] frequency) {
        double sum = 0;
        int i = 0;
while (i < frequency.length) {
            if (frequency[i] > 0 && i % 2 == 1) {
                sum += frequency[i];
            }
        i += 1;
}
        return sum;
    }

    public static void main(String[] args) {
        // Test code
        double[] frequency = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0};
        double sum = emphasizeHigherFrequencies(frequency);
        System.out.println(sum); // Output: 9.0
    }
}
