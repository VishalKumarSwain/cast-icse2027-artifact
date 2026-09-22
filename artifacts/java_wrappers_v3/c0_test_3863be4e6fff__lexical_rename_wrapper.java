import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_3863be4e6fff_t {
public JkCheckSumer appendTo(File archive) {
        final File temp_renamed = JkUtilsFile.tempFile(archive.getName(), "");
        JkUtilsFile.move(archive, temp_renamed);
        final JkCheckSumer jkCheckSumer = this.merge(temp_renamed).to(archive, JkPathFilter.ACCEPT_ALL);
        temp_renamed.delete();
        return jkCheckSumer;
    }
}
