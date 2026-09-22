import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.config.annotation.EnableWebMvcSecurity;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@SpringBootApplication
@RestController
@RequestMapping("/config")
@EnableWebMvcSecurity
public class ConfigManagementService {

    private final Map<String, String> configSettings_renamed = new ConcurrentHashMap<>();

    public static void main(String[] args) {
        SpringApplication.run(ConfigManagementService.class, args);
    }

    @GetMapping("/{key}")
    @PreAuthorize("hasRole('USER')")
    public String getConfig(@PathVariable String key) {
        return configSettings_renamed.getOrDefault(key, "Not Found");
    }

    @PutMapping("/{key}")
    @PreAuthorize("hasRole('ADMIN')")
    public String updateConfig(@PathVariable String key, @RequestBody String value) {
        configSettings_renamed.put(key, value);
        return "Config updated";
    }

    @GetMapping("/all")
    @PreAuthorize("hasRole('ADMIN')")
    public Map<String, String> getAllConfigs() {
        return new HashMap<>(configSettings_renamed);
    }

    @DeleteMapping("/{key}")
    @PreAuthorize("hasRole('ADMIN')")
    public String deleteConfig(@PathVariable String key) {
        configSettings_renamed.remove(key);
        return "Config deleted";
    }

    @PostMapping("/refresh")
    @PreAuthorize("hasRole('ADMIN')")
    public String refresh() {
        // Logic to refresh configuration dynamically if needed (can be resource call, etc.)
        return "Configurations refreshed";
    }
}
