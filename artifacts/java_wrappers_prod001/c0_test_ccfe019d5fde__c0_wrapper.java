import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_ccfe019d5fde {
private String createPublicStorageFilePath()
    {
        logFileDirectoryPath = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS) + "/" + logDirectoryName + "/";
        String filePath = logFileDirectoryPath +
                fileNamePrefix + SurveyRecordProcessor.DATE_TIME_FORMATTER.format(LocalDateTime.now()) + ".gpkg";
        int counter = 0;
        while (new File(filePath).exists())
        {
            counter++;
            filePath = logFileDirectoryPath + fileNamePrefix +
                    SurveyRecordProcessor.DATE_TIME_FORMATTER.format(LocalDateTime.now()) + "-" + counter + ".gpkg";
        }
        return filePath;
    }
}
