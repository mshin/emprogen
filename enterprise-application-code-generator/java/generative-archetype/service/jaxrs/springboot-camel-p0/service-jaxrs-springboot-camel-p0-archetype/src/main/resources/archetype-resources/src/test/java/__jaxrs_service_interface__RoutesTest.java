package ${package};

import org.apache.camel.Endpoint;
import org.apache.camel.Exchange;
import org.apache.camel.Producer;
import org.apache.camel.builder.AdviceWithRouteBuilder;
import org.apache.camel.builder.ExchangeBuilder;
import org.apache.camel.component.mock.MockEndpoint;
import org.apache.camel.model.ModelCamelContext;
import org.apache.camel.test.spring.CamelSpringBootRunner;
import org.apache.camel.test.spring.DisableJmx;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.annotation.DirtiesContext.ClassMode;

/**
 * @author ${author}
 */
@RunWith(CamelSpringBootRunner.class)
@SpringBootTest
@DirtiesContext(classMode = ClassMode.AFTER_EACH_TEST_METHOD)
@DisableJmx(true)
public class ${jaxrs_service_interface}RoutesTest {

    public static final Logger LOGGER = LoggerFactory.getLogger(${jaxrs_service_interface}RoutesTest.class.getName());

    @Autowired
    ModelCamelContext camelContext;
    MockEndpoint mockOutputEndpoint;
    Endpoint mockFromEndpoint;

    @Before
    public void before() throws Exception {

        camelContext.getRouteDefinition("${jaxrs_service_interface}Route").adviceWith(camelContext, new AdviceWithRouteBuilder() {
            public void configure() throws Exception {
                this.weaveAddLast().to("mock:output");
                this.replaceFromWith("direct:mock");
            }
        });

        mockFromEndpoint = camelContext.getEndpoint("direct:mock");
        mockOutputEndpoint = camelContext.getEndpoint("mock:output", MockEndpoint.class);

    }

    @Test
    public void runRouteTest() throws Exception {
        Producer producer = mockFromEndpoint.createProducer();
        Exchange exchange = ExchangeBuilder.anExchange(camelContext).withBody("test").build();
        producer.process(exchange);
        mockOutputEndpoint.expectedMessageCount(1);
        mockOutputEndpoint.assertIsSatisfied();
    }

}
