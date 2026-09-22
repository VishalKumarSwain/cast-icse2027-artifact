import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_01a97b1685ca {
@Test
    public void testHyperbolic() throws FactoryException, TransformException {
        createCompleteProjection(method(true),
                317063.667,                             
                317063.667 * (20854895./20926202),      
                179 + 20./60,                           
                -(16 + 15./60),                         
                NaN,                                    
                NaN,                                    
                NaN,                                    
                12513.318,                              
                16628.885);                             
        final double λ =  179 + (59 + 39.6115/60)/60;   /
        final double φ = -(16 + (50 + 29.2435/60)/60);  /
        final DirectPosition2D p = new DirectPosition2D(λ, φ);
        assertSame(p, transform.transform(p, p));
        assertEquals(16015.2890, p.x, 0.00005);
        assertEquals(13369.6601, p.y, 0.00005);
        assertSame(p, transform.inverse().transform(p, p));
        assertEquals(λ, p.x, Formulas.ANGULAR_TOLERANCE);
        assertEquals(φ, p.y, Formulas.ANGULAR_TOLERANCE);
    }
}
