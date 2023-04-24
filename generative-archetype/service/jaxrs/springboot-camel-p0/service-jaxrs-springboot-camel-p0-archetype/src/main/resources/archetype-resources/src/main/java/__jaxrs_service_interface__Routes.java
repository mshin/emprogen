package ${package};

import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * @author ${author}
 */
@Component
public class ${jaxrs_service_interface}Routes extends RouteBuilder {

    @Autowired
    private ${jaxrs_service_interface}Bean bean;

    @Override
    public void configure() throws Exception {
        // @formatter:off
        from("cxfrs:bean:rsServer?bindingStyle=SimpleConsumer").routeId("${jaxrs_service_interface}Route")
            // .log("headers: ${in.headers}").log("body: ${body}")
            .choice()
                .when(header("operationName").isEqualTo("javaMethod"))
                    //.bean(bean, "javaMethod(${body})")
                    ;
        // @formatter:on

    }

}