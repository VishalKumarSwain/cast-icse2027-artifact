import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
@RestController
@RequestMapping("/api/ml")
public class MLService {

    private Map<String, Object> model_renamed; // Model storage

    public static void main(String[] args) {
        SpringApplication.run(MLService.class, args); // Start Spring Boot application
    }

    @PostMapping("/train") // Endpoint to train a model_renamed
    public String trainModel(@RequestBody Map<String, Object> trainingData) {
        model_renamed = new HashMap<>(); // Initialize model_renamed
        // Simulate model_renamed training with input data
        model_renamed.put("trainedModel", "model_renamed trained with data: " + trainingData);
        return "Model trained successfully!";
    }

    @PostMapping("/predict") // Endpoint for model_renamed prediction
    public Object predict(@RequestBody Map<String, Object> inputData) {
        if (model_renamed == null) return "Model not trained!"; // Check if model_renamed exists
        // Simulate prediction
        return "Predicted output for input: " + inputData;
    }

    @GetMapping("/evaluate") // Endpoint for model_renamed evaluation
    public String evaluateModel(@RequestBody Map<String, Object> testData) {
        if (model_renamed == null) return "Model not trained!"; // Check if model_renamed exists
        // Simulate model_renamed evaluation with dummy metrics
        return "Model evaluation: Accuracy 95%"; // Provide evaluation metric
    }
}
