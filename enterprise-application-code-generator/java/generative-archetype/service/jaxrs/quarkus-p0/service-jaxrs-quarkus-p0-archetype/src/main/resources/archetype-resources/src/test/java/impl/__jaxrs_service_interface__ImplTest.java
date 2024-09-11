package ${package}.impl;

import io.quarkus.test.junit.QuarkusTest;
import io.restassured.response.Response;
import io.restassured.response.ResponseBody;
import static io.restassured.RestAssured.given;

import jakarta.inject.Inject;

import net.minidev.json.JSONObject;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author ${author}
 */
@QuarkusTest
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class ${jaxrs_service_interface}ImplTest {

    public static final Logger LOGGER = LoggerFactory.getLogger(${jaxrs_service_interface}ImplTest.class.getName());

    @Inject
    ${jaxrs_service_interface}Impl impl;

    @ConfigProperty(name = "quarkus.http.host")
    String host;

    @ConfigProperty(name = "quarkus.http.port")
    String port;

    @BeforeAll
    public void before() {

    }

    @Test
    public void test1() {
        LOGGER.info("Start ${jaxrs_service_interface}ImplTest test1");

        given()
        .when().get("/q/openapi")
        .then()
        .statusCode(200);
    }

    @Test
    public void test2() {
        LOGGER.info("Start ${jaxrs_service_interface}ImplTest test2");

        given()
        .when().get("/q/swagger-ui")
        .then()
        .statusCode(200);
    }

    //TODO Comment @Test back in to activate this test after finishing it.
    //TODO Set /TODO_set_rest_path to the relative path tested in this test.
    //@Test
    public void test3() {
        LOGGER.info("Start ${jaxrs_service_interface}ImplTest test3");

        JSONObject requestParams = new JSONObject();
        //TODO Add requestParams
        // requestParams.put("key", "value");

        StringBuilder path = new StringBuilder();
        path.append("http://");
        path.append(host);
        path.append(":");
        path.append(port);
        path.append("/TODO_set_rest_path");

        LOGGER.info("${jaxrs_service_interface}ImplTest requestParams: {}" + requestParams);
        LOGGER.info("path: {}", path.toString());

        Response response = 
        given()
        .body(requestParams.toJSONString())
        .header("Content-Type", "application/json")
        .post("/TODO_set_rest_path");

        LOGGER.info("statusLine: {}", response.getStatusLine());
        LOGGER.info("statusCode: {}", response.getStatusCode());

        Assertions.assertEquals(200, response.getStatusCode());

        ResponseBody body = response.getBody();
        LOGGER.info("body: {}", body.asPrettyString());
        Assertions.assertNotNull(body.asPrettyString());
    }

}
