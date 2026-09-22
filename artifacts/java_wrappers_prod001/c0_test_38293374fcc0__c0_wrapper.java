import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_38293374fcc0 {
public ImplicationalSystem getImplicationalSystem() {
        // other code here...

        // rules generation
        for (ComparableSet jx : family) {
            for (Node j : join) {
                ComparableSet p = new ComparableSet();
                p.add(j.getContent());
                p.addAll(jx);
                if (!family.contains(p)) {
                    ComparableSet min = new ComparableSet();
                    min.addAll(family.last());
                    for (ComparableSet c : family) {
                        //System.out.println("min: "+min.getClass()+" -C:"+C.getClass());
                        if (c.containsAll(p) && !p.containsAll(c) && min.containsAll(c)) {
                            min = c.clone();
                        }
                    }
                    Rule r = new Rule();
                    r.addAllToPremise(p);
                    min.removeAll(p);
                    r.addAllToConclusion(min);
                    sigma.addRule(r);
                }
            }
        }

        // INF-SUP rule generation
        for (Node j : join) {
            for (Node m : meet) {
                if (j.equals(m) || tmp.getSuccessorNodes(j).contains(m)) {
                    Rule r = new Rule();
                    r.addAllToPremise(new ComparableSet(JoinContent.get(j)));
                    r.addAllToConclusion(new ComparableSet(MeetContent.get(m)));
                    sigma.addRule(r);
                }
            }
        }

        // make the system right maximal
        sigma.makeRightMaximal();

        return sigma;
    }

}
