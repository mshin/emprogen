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
import com.github.mshin.exception.response.model.ExceptionResponses;

/**
 * @author MunChul Shin
 */
@Provider
public class ExceptionResponsesHandler implements ExceptionMapper<ExceptionResponses> {

    private static final String CLASS_NAME = ExceptionResponsesHandler.class.getName();
    private static final Logger LOGGER = LoggerFactory.getLogger(CLASS_NAME);

    @Context
    private HttpHeaders headers;

    @Override
    public Response toResponse(ExceptionResponses exceptionResponses) {

        ExceptionResponseUtil.sortExceptionResponses(exceptionResponses);

        ExceptionResponseUtil.logExceptionResponses(LOGGER, exceptionResponses);

        ExceptionResponse topResponse = null;
        Response.Status httpStatus = null;
        if (null != exceptionResponses && null != exceptionResponses.getExceptionResponses()
                && null != exceptionResponses.getExceptionResponses().get(0)) {
            topResponse = exceptionResponses.getExceptionResponses().get(0);
        }

        if (null != topResponse && null != topResponse.getHttpStatus()) {
            httpStatus = topResponse.getHttpStatus();
        } else {
            httpStatus = Response.Status.NO_CONTENT;
        }

        ResponseBuilder rb = Response.status(httpStatus).entity(exceptionResponses);

        return rb.build();
    }

}
