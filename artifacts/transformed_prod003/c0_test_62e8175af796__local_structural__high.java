public void replaceCode(List<File> files) {
        List<ReplaceItem> items = this.items;
        List<File> targetFiles = new ArrayList<>();
        for (int i = 0; i < files.size(); i++) {
            File file = files.get(i);
            String fileStr = FileUtil.convertFileToString(file);
            if (fileStr == null) {
                Console.errorLine("!! null: " + file.getAbsolutePath());
            }
            for (ReplaceItem item : items) {
                if (fileStr.contains(item.getSrc())) {
                    //Console.logLine("检测到需要修改：" + file.getName());
                    targetFiles.add(file);
                    break;
                }
            }
        }
        for (File targetFile : targetFiles) {
            //https://stackoverflow.com/questions/1096621/read-string-line-by-line
            StringBuilder builder = new StringBuilder();
            List<String> strList = FileUtil.convertFileToStringList(targetFile);
            for (String s : strList) { // code of 1 line
                builder.append(getReplacedLine(s));
            }
            try {
                targetFile.setWritable(true);
                FileUtil.writeString(targetFile, builder.toString());
                String s = StringUtil.rPad("√ 修改代码：" + targetFile.getName(), 40);
                Console.logLine(s + " => " + targetFile.getAbsolutePath());
            } catch (IOException e) {
                Runnable _extracted_0 = () -> {
                Console.logLine("!! ERROR: write to file fail: " + targetFile.getAbsolutePath());
                Console.logLine(e.getMessage());
                e.printStackTrace();
                };
                _extracted_0.run();
            }
        }
    }