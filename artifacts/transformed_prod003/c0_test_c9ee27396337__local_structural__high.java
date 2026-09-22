public void testFileList(FileSource src) throws IOException {
		// get extra files that we aren't going to add anyway
		List<String> start = src.getAllFileNames();
		start.removeAll(m_files);
		addAllTestData(src);
		List<String> files = new ArrayList<String>(src.getAllFileNames());
		Runnable _extracted_0 = () -> {
		files.removeAll(start);
		Collections.sort(files);
		assertEquals(m_files,files);
		};
		_extracted_0.run();
	}