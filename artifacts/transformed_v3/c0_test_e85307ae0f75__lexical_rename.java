public class MultiFileWordCount {
  public static void main(String[] args) throws Exception {
    if (args.length != 2) {
      System.err.println("Usage: MultiFileWordCount <input directory> <output file>");
      System.exit(1);
    }

    String inputDir_renamed = args[0];
    String outputFile = args[1];

    FileOutputFormat.setOutputPath(new Path(outputFile));

    FileInputFormat.addInputPath(new Path(inputDir_renamed));

    Job job = new Job();
    job.setJarByClass(MultiFileWordCount.class);
    job.setJobName("MultiFileWordCount");

    MultipleFileInputFormat.setMultipleMapOutputFormatClass(job, TextOutputFormat.class);

    MultipleFileInputFormat.setInputFormatClass(job, MultiFileInputFormat.class);

    MultipleFileInputFormat.setOutputFormatClass(job, TextOutputFormat.class);

    MultipleFileInputFormat.setInputFileClass(job, TextInputFileFormat.class);

    MultipleFileInputFormat.setOutputFileClass(job, TextOutputFileFormat.class);

    MultipleFileInputFormat.setOutputMapClass(job, MapOutputFormat.class);

    job.setMapperClass(WordCountMapper.class);

    job.setReducerClass(WordCountReducer.class);

    job.setOutputKeyClass(Text.class);

    job.setOutputValueClass(IntWritable.class);

    FileSystem fs = FileSystem.get(new Configuration());
    fs.delete(new Path(outputFile), true);

    job.setNumReduceTasks(1);

    job.setPartitionerClass(Partitioner.class);

    job.setInputFormatClass(CombineFileInputFormat.class);

    CombineFileInputFormat.setInputFiles(job, FileInputFormat.getInputPaths());

    CombineFileInputFormat.setOutputFormat(job, TextOutputFormat.class);

    job.setOutputFormat(TextOutputFormat.class);

    job.setOutputKeyClass(Text.class);

    job.setOutputValueClass(IntWritable.class);

    fs.delete(new Path(outputFile), true);

    job.execute();
  }
}
