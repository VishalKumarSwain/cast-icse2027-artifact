private String createPublicStorageFilePath()
    {
        logFileDirectoryPath_renamed = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS) + "/" + logDirectoryName + "/";
        String filePath = logFileDirectoryPath_renamed +
                fileNamePrefix + SurveyRecordProcessor.DATE_TIME_FORMATTER.format(LocalDateTime.now()) + ".gpkg";
        int counter = 0;
        while (new File(filePath).exists())
        {
            counter++;
            filePath = logFileDirectoryPath_renamed + fileNamePrefix +
                    SurveyRecordProcessor.DATE_TIME_FORMATTER.format(LocalDateTime.now()) + "-" + counter + ".gpkg";
        }
        return filePath;
    }