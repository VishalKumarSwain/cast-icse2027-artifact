import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_3863be4e6fff {
public JkCheckSumer appendTo(File archive) {
        final File temp = JkUtilsFile.tempFile(archive.getName(), "");
        JkUtilsFile.move(archive, temp);
        final JkCheckSumer jkCheckSumer = this.merge(temp).to(archive, JkPathFilter.ACCEPT_ALL);
        temp.delete();
        return jkCheckSumer;
    }
}
