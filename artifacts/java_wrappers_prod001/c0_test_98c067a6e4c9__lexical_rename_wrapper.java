import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_98c067a6e4c9_t {
public static Set<Method> retrieveMethods (final Class<?> objClass, final Class<? extends Annotation> annotationClass) {
		final Set<Method> methods_renamed = new HashSet<>();
		for (final Method method : objClass.getMethods()) {
			if (annotationClass == null || method.getAnnotation(annotationClass) != null) {
				if (LG.isLoggable(Level.FINE)) {
					LG.fine("Added method: " + method.getName());
				}
				methods_renamed.add(method);
			}
		}
		return methods_renamed;
	}
}
