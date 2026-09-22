package org.df4j.tricky.charflow;

import org.df4j.core.actor.Actor;
import org.df4j.core.port.InpChars;
import org.df4j.core.port.OutFlow;

public abstract class Scanner extends Actor {
  public InpChars inp = new InpChars(this);
  public OutFlow outp = new OutFlow<>(this);
}
