package ${package};

import java.util.Arrays;

import org.apache.cxf.Bus;
import org.apache.cxf.jaxrs.JAXRSServerFactoryBean;
import org.apache.cxf.jaxrs.swagger.Swagger2Feature;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

// import com.fasterxml.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import com.fasterxml.jackson.jaxrs.json.JacksonJsonProvider;
import ${jaxrs_service_package}.${jaxrs_service_interface};

/**
 * @author ${author}
 */
@SpringBootApplication
public class Application {

    @Autowired
    private Bus bus;

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    public JAXRSServerFactoryBean rsServer() {
        JAXRSServerFactoryBean factoryBean = new JAXRSServerFactoryBean();
        factoryBean.setBus(bus);
        factoryBean.setAddress("/");
        factoryBean.setProviders(Arrays.asList(new JacksonJsonProvider()));
        factoryBean.setFeatures(Arrays.asList(swagger2Feature()));
        factoryBean.setServiceClass(${jaxrs_service_interface}.class);
        return factoryBean;
    }

    @Bean
    public Swagger2Feature swagger2Feature() {
        Swagger2Feature feature = new Swagger2Feature();
        feature.setRunAsFilter(true);
        return feature;
    }
}