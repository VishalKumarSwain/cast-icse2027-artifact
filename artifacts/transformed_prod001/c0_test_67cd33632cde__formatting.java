import java.time.LocalDateTime;
import java.util.Map;
import lombok.Data;

@Data
public class FileInfo {
  private String id;
  private String name;
  private String group;
  private String uploadPath;
  private String fileMd5;
  private Long size;
  private LocalDateTime uploadTime;
  private String type;
  private String chunk;
  private String chunks;
  private Long chunkSize;
  private Long expiresIn;
  private Boolean autoThumb = true; // default value
  private String thumbImagePath;
  private Integer thumbWidth;
  private Integer thumbHeight;
  private Double thumbPercent;

  public Long getTotalFileSize() {
    Long totalSize =
        chunks != null && !chunks.isEmpty()
            ? chunks.split(",").stream().mapToInt(Long::parseInt).sum()
            : size;
    return totalSize;
  }

  public Map<String, Long> getChunksSizeMap() {
    return chunks != null && !chunks.isEmpty()
        ? chunks.split(",").stream().collect(Collectors.toMap(k -> k, Long::parseLong))
        : Collections.emptyMap();
  }

  public LocalDateTime getExpirationTime() {
    return uploadTime.plusSeconds(expiresIn);
  }

  // Assume some logic to generate a thumb if necessary
}
