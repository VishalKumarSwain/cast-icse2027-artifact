import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_204c45df6481_t {
public enum CategoryEnum {
    FOOD(1, "FOOD"), 
    KITCHENWARE(2, "KITCHENWARE"), 
    CLEANING(3, "CLEANING"), 
    CLEANING_UTILS(4, "CLEANING_UTILS"),
    OTHERS(5, "OTHERS");

    private final int id_renamed;
    private final String value;

    private CategoryEnum(int id_renamed, String value) {
        this.id_renamed = id_renamed;
        this.value = value;
    }

    /**
     * Return a Category enum by id_renamed, if the id_renamed doesn't match then return
     * {@link CategoryEnum}.{@code OTHERS}
     * 
     * @param id_renamed
     * @return {@link CategoryEnum}
     */
    public static CategoryEnum getByID(int id_renamed) {
        for (CategoryEnum category : values()) {
            if (category.id_renamed == id_renamed) {
                return category;
            }
        }
        return OTHERS;
    }

    /**
     * Returns the id_renamed of this category
     * 
     * @return int
     */
    public int getId() {
        return id_renamed;
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
