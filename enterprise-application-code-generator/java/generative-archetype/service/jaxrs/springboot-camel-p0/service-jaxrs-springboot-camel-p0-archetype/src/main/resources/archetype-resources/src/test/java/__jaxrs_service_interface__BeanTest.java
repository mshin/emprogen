package ${package};

import static org.junit.Assert.assertTrue;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

/**
 * @author ${author}
 */
@RunWith(SpringRunner.class)
@SpringBootTest
public class ${jaxrs_service_interface}BeanTest {

    public static final Logger LOGGER = LoggerFactory.getLogger(${jaxrs_service_interface}BeanTest.class.getName());

    @Autowired
    ${jaxrs_service_interface}Bean bean;

    @Test
    public void test() {

    }
}
