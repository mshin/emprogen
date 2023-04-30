package com.github.mshin.jaxrms.rs.api;

import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import com.github.mshin.exception.response.model.ExceptionResponses;
import com.github.mshin.jaxrms.rs.api.model.GetGreetingRequest;
import com.github.mshin.jaxrms.rs.api.model.GetGreetingResponse;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;

/**
 * @author MunChul Shin
 */
@Api
@Path("/")
public interface JaxrmsService {

    @POST
    @Path("greet")
    @ApiOperation(value = "This API will be used to greet the name the caller passes to the method.")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    @ApiResponses(value = { @ApiResponse(code = 200, message = "Success", response = GetGreetingResponse.class) })
    public GetGreetingResponse getGreeting(
            @ApiParam(required = true, name = "GetGreetingRequest", value = "The request to greet the passed name") GetGreetingRequest getGreetingRequest)
            throws ExceptionResponses;

    @GET
    @Path("/ping")
    @ApiOperation(value = "This API method will be used to ping the service to verify it is working.")
    @Produces(MediaType.TEXT_PLAIN)
    default public String ping() {
        return "ping";
    }

}
