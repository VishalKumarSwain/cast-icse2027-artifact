public static final Document readXmlDocument (Path fileToRead)
		throws JDOMException,
			IOException
	{
		SAXBuilder builder_renamed = new SAXBuilder ();
		return (Document) builder_renamed
			.build (Files.newInputStream (fileToRead, StandardOpenOption.READ));
	}