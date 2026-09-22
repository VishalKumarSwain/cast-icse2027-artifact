import org.springframework.beans.BeansException;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;

public class ContentTypeResolverService implements ApplicationContextAware {

  private ApplicationContext context;

  @Override
  public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
    this.context = applicationContext;
  }

  public <T extends RequestedContentTypeResolver> T getFirstContentTypeResolver(
      Class<T> resolverType) {
    Map<String, T> resolvers = context.getBeansOfType(resolverType);
    return resolvers.isEmpty() ? null : resolvers.values().iterator().next();
  }
}
