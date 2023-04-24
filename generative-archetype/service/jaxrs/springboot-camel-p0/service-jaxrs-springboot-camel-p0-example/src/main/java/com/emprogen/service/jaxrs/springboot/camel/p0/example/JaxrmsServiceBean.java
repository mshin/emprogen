package com.emprogen.service.jaxrs.springboot.camel.p0.example;

import org.springframework.stereotype.Component;

import com.github.mshin.exception.response.model.ExceptionResponses;
import com.github.mshin.jaxrms.rs.api.JaxrmsService;
import com.github.mshin.jaxrms.rs.api.model.GetGreetingRequest;
import com.github.mshin.jaxrms.rs.api.model.GetGreetingResponse;

@Component
public class JaxrmsServiceBean implements JaxrmsService {

    public GetGreetingResponse getGreeting(GetGreetingRequest getGreetingRequest) throws ExceptionResponses {
        GetGreetingResponse response = new GetGreetingResponse();
        response.setResponseCode(0);
        response.setGreeting("Hi " + getGreetingRequest.getName() + "!");
        return response;
    }

}