package com.github.mshin.exception.response.handler;

import javax.ws.rs.core.Context;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.ResponseBuilder;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.github.mshin.exception.response.model.ExceptionResponse;

/**
 * @author MunChul Shin
 */
@Provider
public class ExceptionResponseHandler implements ExceptionMapper<ExceptionResponse> {

    private static final String CLASS_NAME = ExceptionResponseHandler.class.getName();
    private static final Logger LOGGER = LoggerFactory.getLogger(CLASS_NAME);

    @Context
    private HttpHeaders headers;

    @Override
    public Response toResponse(ExceptionResponse exceptionResponse) {

        ExceptionResponseUtil.logExceptionResponse(LOGGER, exceptionResponse);

        Response.Status httpStatus = null;
        if (null != exceptionResponse && null != exceptionResponse.getHttpStatus()) {
            httpStatus = exceptionResponse.getHttpStatus();
        } else {
            httpStatus = Response.Status.NO_CONTENT;
        }

        ResponseBuilder rb = Response.status(httpStatus).entity(exceptionResponse);

        return rb.build();
    }

}
