package ${package};

import io.quarkus.test.junit.QuarkusTest;

import jakarta.inject.Inject;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author ${author}
 */
@QuarkusTest
public class ${jaxrs_service_interface}ServiceTest {

    public static final Logger LOGGER = LoggerFactory.getLogger(${jaxrs_service_interface}ServiceTest.class.getName());

    @Inject
    ${jaxrs_service_interface}Service service;

    @Test
    public void test1() {
        LOGGER.info("Start ${jaxrs_service_interface}ServiceTest test1");

    }
}
