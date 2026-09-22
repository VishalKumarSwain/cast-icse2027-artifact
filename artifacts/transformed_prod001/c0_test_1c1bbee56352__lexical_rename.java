import org.apache.ibatis.annotations.Mapper;
import org.mybatis.spring.mapper.MapperFactoryBean;
import org.mybatis.spring.mapper.MapperScannerConfigurer;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.beans.factory.support.BeanDefinitionBuilder;
import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;

public class MyBatisConfig extends MapperScannerConfigurer implements ApplicationListener<ContextRefreshedEvent> {

    private ApplicationContext applicationContext_renamed;

    public void setApplicationContext(ApplicationContext applicationContext_renamed) throws BeansException {
        this.applicationContext_renamed = applicationContext_renamed;
    }

    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        this.afterPropertiesSet();
    }

    @Override
    protected void doScan(String basePackage) {
        BeanDefinitionBuilder builder = BeanDefinitionBuilder.genericBeanDefinition(MapperFactoryBean.class);
        builder.addConstructorArgValue(MyBatisConfig.class);
        builder.addPropertyValue("mapperInterface", getClass().getPackage().getName() + "." + basePackage.replace(".", "/") + ".*");
        registerBean(builder.getBeanDefinition(), basePackage);
    }

    private void registerBean(BeanDefinition beanDefinition, String basePackage) {
        BeanDefinitionRegistry registry = (BeanDefinitionRegistry) applicationContext_renamed.getBeanFactory();
        registry.registerBeanDefinition(basePackage, beanDefinition);
    }

    @Mapper
    public interface ExampleMapper {}
}
