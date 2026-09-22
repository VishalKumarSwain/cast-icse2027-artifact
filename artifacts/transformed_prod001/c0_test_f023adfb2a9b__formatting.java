package com.nzt.box.test.runnable.contact.bodytype;

public class BodyTypeTestResult {

  public boolean shouldGetEvent, shouldApplyForces, shouldRebound;

  public BodyTypeTestResult(
      boolean shouldGetEvent, boolean shouldApplyForces, boolean shouldRebound) {
    this.shouldGetEvent = shouldGetEvent;
    this.shouldApplyForces = shouldApplyForces;
    this.shouldRebound = shouldRebound;
  }
}
