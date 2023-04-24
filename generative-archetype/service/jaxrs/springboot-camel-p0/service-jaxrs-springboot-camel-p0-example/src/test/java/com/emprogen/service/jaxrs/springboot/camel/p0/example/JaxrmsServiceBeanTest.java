package com.emprogen.service.jaxrs.springboot.camel.p0.example;

import static org.junit.Assert.assertTrue;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import com.emprogen.service.jaxrs.springboot.camel.p0.example.JaxrmsServiceBean;
import com.github.mshin.jaxrms.rs.api.model.GetGreetingRequest;
import com.github.mshin.jaxrms.rs.api.model.GetGreetingResponse;

/**
 * 
 * @author MunChul Shin
 *
 */
@RunWith(SpringRunner.class)
@SpringBootTest
public class JaxrmsServiceBeanTest {

    public static final Logger LOGGER = LoggerFactory.getLogger(JaxrmsServiceBeanTest.class.getName());

    @Autowired
    JaxrmsServiceBean bean;

    @Test
    public void getGreetingTest() {
        GetGreetingRequest request = new GetGreetingRequest();
        request.setName("Me");
        GetGreetingResponse response = bean.getGreeting(request);

        assertTrue(response.getResponseCode().equals(0));
        assertTrue(response.getGreeting().equals("Hi Me!"));
    }
}
