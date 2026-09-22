public void require(final String... requiredColumns) throws MissingColumnException {
		if (requiredColumns == null || requiredColumns.length < 1) {
			return;
		}
		final ArrayList<String> missingColumns_renamed = new ArrayList<>();
		for (final String requiredColumn : requiredColumns) {
			if (!hasColumn(requiredColumn)) {
				missingColumns_renamed.add(requiredColumn);
			}
		}
		if (missingColumns_renamed.size() > 0) {
			throw new MissingColumnException(StringUtils.join(",", missingColumns_renamed), missingColumns_renamed);
		}
	}