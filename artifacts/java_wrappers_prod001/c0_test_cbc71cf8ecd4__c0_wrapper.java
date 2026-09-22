import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_cbc71cf8ecd4 {
public void require(final String... requiredColumns) throws MissingColumnException {
		if (requiredColumns == null || requiredColumns.length < 1) {
			return;
		}
		final ArrayList<String> missingColumns = new ArrayList<>();
		for (final String requiredColumn : requiredColumns) {
			if (!hasColumn(requiredColumn)) {
				missingColumns.add(requiredColumn);
			}
		}
		if (missingColumns.size() > 0) {
			throw new MissingColumnException(StringUtils.join(",", missingColumns), missingColumns);
		}
	}
}
