import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_850204e47168_t {
@Test
public void testConnectionsAPI() {
    // first, we set up our test server_renamed
    Server server_renamed = new Server();
    server_renamed.makeTransactional();
    server_renamed.start();
    assert server_renamed.isStarted();
    // we make requests
    Connection connection = JerseyClientFactory.create().getConnection();
    String url = "http://localhost:8080/connections";
    
    // verify that we hit the right address
    assertEquals("Wrong single endpoint address", url, connection.getClientURI());
    // verify that we can make GET, POST, DELETE
    Response responseGET =  connection.get(Entity.text("Some data"));
    assertEquals("GET request failed", 200, responseGET.getStatus());
      
    Response responsePOST = connection.post(Entity.text("Some data"));
    assertEquals("POST request failed", 201, responsePOST.getStatus());
    
    Response responseDELETE = connection.delete();
    assertEquals("DELETE request failed", 200, responseDELETE.getStatus());
}

}
