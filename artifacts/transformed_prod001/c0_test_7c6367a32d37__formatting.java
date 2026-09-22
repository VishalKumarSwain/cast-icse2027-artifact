import java.util.List;
import org.springframework.data.repository.query.Param;

// Assuming this is an interface in your service or repository layer
public interface ProductionPlanService {

  // Method to retrieve production plans or product IDs associated with a given materielId
  List<String> planProductId(@Param("materielId") String materielId);

  // Method to add a new production plan
  ProductionPlan addProductionPlan(ProductionPlan productionPlan);
}

// Assuming the ProductionPlan class is defined as follows
class ProductionPlan {
  private String id;
  private String materielId;
  private int quantity;
  private String dueDate;
  // getters and setters
  // constructors if needed
  // other relevant fields
}
