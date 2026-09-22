package com.brauch.brauch.service;

import org.springframework.stereotype.Service;

@Service
public class RestService {

  // Example: Inject a repository if needed
  // @Autowired
  // private SomeRepository someRepository;

  /**
   * Example method for a service operation.
   *
   * @return a result from your business logic.
   */
  public String exampleServiceMethod() {
    // Business logic goes here
    System.out.println("Executing example service method");
    return "Service method executed successfully!";
  }
}
