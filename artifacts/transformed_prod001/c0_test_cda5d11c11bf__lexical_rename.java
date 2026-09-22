import org.springframework.beans.BeansException;
import org.springframework.context_renamed.ApplicationContext;
import org.springframework.context_renamed.ApplicationContextAware;

public class ContentTypeResolverService implements ApplicationContextAware {

    private ApplicationContext context_renamed;

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.context_renamed = applicationContext;
    }

    public <T extends RequestedContentTypeResolver> T getFirstContentTypeResolver(Class<T> resolverType) {
        Map<String, T> resolvers = context_renamed.getBeansOfType(resolverType);
        return resolvers.isEmpty() ? null : resolvers.values().iterator().next();
    }
}
