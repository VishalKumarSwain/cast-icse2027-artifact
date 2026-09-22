import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_d7b0c08b019c_t {
public static final Document readXmlDocument (Path fileToRead)
		throws JDOMException,
			IOException
	{
		SAXBuilder builder_renamed = new SAXBuilder ();
		return (Document) builder_renamed
			.build (Files.newInputStream (fileToRead, StandardOpenOption.READ));
	}
}
