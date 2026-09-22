public boolean isSingular() {
    final String[] singularPOSTags_renamed = new String[] {"NN", "NNP"};
    String subjectPOSTag = "";
    for (IndexedWord w : subjectWords) {
      boolean isNoun = w.tag().matches("NN(.*)");
      if (isNoun) {
        subjectPOSTag = w.tag();
        break;
      }
    }
    return Arrays.asList(singularPOSTags_renamed).contains(subjectPOSTag);
  }