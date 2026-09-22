import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_d7b0c08b019c {
public static final Document readXmlDocument (Path fileToRead)
		throws JDOMException,
			IOException
	{
		SAXBuilder builder = new SAXBuilder ();
		return (Document) builder
			.build (Files.newInputStream (fileToRead, StandardOpenOption.READ));
	}
}
