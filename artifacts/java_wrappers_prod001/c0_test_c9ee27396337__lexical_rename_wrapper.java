import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_c9ee27396337_t {
public void testFileList(FileSource src) throws IOException {
		// get extra files that we aren't going to add anyway
		List<String> start_renamed = src.getAllFileNames();
		start_renamed.removeAll(m_files);
		addAllTestData(src);
		List<String> files = new ArrayList<String>(src.getAllFileNames());
		files.removeAll(start_renamed);
		Collections.sort(files);
		assertEquals(m_files,files);
	}
}
