import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_204c45df6481_t {
public enum CategoryEnum {
  FOOD(1, "FOOD"),
  KITCHENWARE(2, "KITCHENWARE"),
  CLEANING(3, "CLEANING"),
  CLEANING_UTILS(4, "CLEANING_UTILS"),
  OTHERS(5, "OTHERS");

  private final int id;
  private final String value;

  private CategoryEnum(int id, String value) {
    this.id = id;
    this.value = value;
  }

  /**
   * Return a Category enum by id, if the id doesn't match then return {@link CategoryEnum}.{@code
   * OTHERS}
   *
   * @param id
   * @return {@link CategoryEnum}
   */
  public static CategoryEnum getByID(int id) {
    for (CategoryEnum category : values()) {
      if (category.id == id) {
        return category;
      }
    }
    return OTHERS;
  }

  /**
   * Returns the id of this category
   *
   * @return int
   */
  public int getId() {
    return id;
  }

  /**
   * Returns the value of this category
   *
   * @return String
   */
  public String getValue() {
    return value;
  }
}

}
