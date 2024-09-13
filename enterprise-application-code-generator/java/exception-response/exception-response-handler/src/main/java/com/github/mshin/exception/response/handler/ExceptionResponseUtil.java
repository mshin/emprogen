package com.github.mshin.exception.response.handler;

import javax.ws.rs.core.Response.Status;

import org.slf4j.Logger;

import com.github.mshin.exception.response.model.ExceptionResponse;
import com.github.mshin.exception.response.model.ExceptionResponses;

/**
 * @author MunChul Shin
 */
public class ExceptionResponseUtil {

    private ExceptionResponseUtil() {
    }

    /**
     * Sort Exceptions from highest to lowest http status code.
     */
    public static void sortExceptionResponses(ExceptionResponses exceptionResponses) {

        if (null == exceptionResponses || null == exceptionResponses.getExceptionResponses()) {
            return;
        }

        exceptionResponses.getExceptionResponses().sort((ExceptionResponse er1,
                ExceptionResponse er2) -> er2.getHttpStatus().getStatusCode() - er1.getHttpStatus().getStatusCode());
    }

    /**
     * Logs at a level coincident with the http status code.
     */
    public static void logExceptionResponse(Logger logger, ExceptionResponse exceptionResponse) {
        Status httpStatus = null;

        String errorString = null;

        if (null != exceptionResponse) {
            errorString = exceptionResponse.getDescription();
        } else {
            errorString = "Unknown exceptionResponse";
        }
        if (null != exceptionResponse && null != exceptionResponse.getHttpStatus()) {
            httpStatus = exceptionResponse.getHttpStatus();
        }
        if (null == httpStatus || null == httpStatus.getFamily()) {
            logger.error("{} exception with indeterminable httpStatus: {}.",
                    ExceptionResponseHandler.class.getSimpleName(), errorString);
        } else {
            switch (httpStatus.getFamily()) {
            case SUCCESSFUL:
                logger.warn("{} exception for SUCCESSFUL response: {}", ExceptionResponseHandler.class.getSimpleName(),
                        errorString);
                break;
            case CLIENT_ERROR:
                logger.error("{} exception for CLIENT_ERROR response: {}",
                        ExceptionResponseHandler.class.getSimpleName(), errorString);
                break;
            case SERVER_ERROR:
                logger.error("{} exception for SERVER_ERROR response: {}",
                        ExceptionResponseHandler.class.getSimpleName(), errorString);
                break;
            default:
                logger.warn("{} default exception: {}", ExceptionResponseHandler.class.getSimpleName(), errorString);
            }
        }
    }

    public static void logExceptionResponses(Logger logger, ExceptionResponses exceptionResponses) {
        if (null != exceptionResponses && null != exceptionResponses.getExceptionResponses()) {
            for (ExceptionResponse er : exceptionResponses.getExceptionResponses()) {
                logExceptionResponse(logger, er);
            }
        }
    }
}