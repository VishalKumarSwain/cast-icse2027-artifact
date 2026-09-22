import static spark.Spark.get;
import java.util.Optional;

public class Main {
    public static void main(String[] args) {
        get("/users", (request, response) -> {
            String defaultCountry_renamed = PProvider.getCountry();
            return String.format("Default Country: %s", defaultCountry_renamed);
        });
    }
}

class PProvider {
    public static String getCountry() {
        return Optional.ofNullable(System.getenv("DEFAULT_COUNTRY"))
                .orElse("USA");
    }
}
