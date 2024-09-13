package com.github.mshin.exception.response.factory;

import javax.ws.rs.core.Response;

import com.github.mshin.exception.response.model.ExceptionResponse;

/**
 * For specific business domains, please subclass this class with domain
 * specific exceptions to allow for business tailored exceptions. Reserve this
 * class for generic, common exception class types.
 * 
 * @author MunChul Shin
 */
public class ExceptionResponseFactory {

    private static final String EXCEPTION_TYPE_SERVER_ERROR = "serverError";
    private static final String EXCEPTION_TYPE_VALIDATION_FAILURE = "validationFailure";
    private static final String EXCEPTION_TYPE_INVALID_REQUEST = "invalidRequest";
    private static final String EXCEPTION_TYPE_NO_CONTENT = "noContent";
    private static final String EXCEPTION_TYPE_RECORD_NOT_FOUND = "recordNotFound";

    private static final String EXCEPTION_MSG_NULL_CLIENT_REQUEST = "Null request from client.";
    private static final String EXCEPTION_MSG_INVALID_REQUEST = "The request was invalid.";
    private static final String EXCEPTION_MSG_RESPONSE_REQUIRED_FOR_FIELD = "No response given for a required field.";

    protected ExceptionResponseFactory() {
    }

    // Common Technical Exceptions

    // status 500
    public static ExceptionResponse createInternalServerErrorExceptionResponse(String technicalDetails) {

        return new ExceptionResponse(Response.Status.INTERNAL_SERVER_ERROR, EXCEPTION_TYPE_SERVER_ERROR, null, null,
                technicalDetails, null);
    }

    // status 500
    public static ExceptionResponse createInternalServerErrorExceptionResponse(String technicalDetails, Throwable e) {

        return new ExceptionResponse(Response.Status.INTERNAL_SERVER_ERROR, EXCEPTION_TYPE_SERVER_ERROR, null, null,
                technicalDetails, null, e);
    }

    // status 500
    public static ExceptionResponse createInternalServerErrorExceptionResponse(String technicalDetails,
            String moreInfo) {

        return new ExceptionResponse(Response.Status.INTERNAL_SERVER_ERROR, EXCEPTION_TYPE_SERVER_ERROR, null, null,
                technicalDetails, moreInfo);
    }

    // status 500
    public static ExceptionResponse createInternalServerErrorExceptionResponse(String technicalDetails, String moreInfo,
            Throwable e) {

        return new ExceptionResponse(Response.Status.INTERNAL_SERVER_ERROR, EXCEPTION_TYPE_SERVER_ERROR, null, null,
                technicalDetails, moreInfo, e);
    }

    // status 400
    public static ExceptionResponse createNullRequestExceptionResponse(String moreInfo) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, EXCEPTION_MSG_NULL_CLIENT_REQUEST, moreInfo);
    }

    // status 400
    public static ExceptionResponse createNullRequestExceptionResponse(String moreInfo, Throwable e) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, EXCEPTION_MSG_NULL_CLIENT_REQUEST, moreInfo, e);
    }

    // status 400
    public static ExceptionResponse createNullRequestExceptionResponse() {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, EXCEPTION_MSG_NULL_CLIENT_REQUEST, null);
    }

    // status 400
    public static ExceptionResponse createNullRequestExceptionResponse(Throwable e) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, EXCEPTION_MSG_NULL_CLIENT_REQUEST, null, e);
    }

    // status 400
    public static ExceptionResponse createBadRequestExceptionResponse(String technicalDetails) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, technicalDetails, null);
    }

    // status 400
    public static ExceptionResponse createBadRequestExceptionResponse(String technicalDetails, Throwable e) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, technicalDetails, null, e);
    }

    // status 400
    public static ExceptionResponse createBadRequestExceptionResponse(String technicalDetails, String moreInfo) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, technicalDetails, moreInfo);
    }

    // status 400
    public static ExceptionResponse createBadRequestExceptionResponse(String technicalDetails, String moreInfo,
            Throwable e) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_INVALID_REQUEST,
                EXCEPTION_MSG_INVALID_REQUEST, null, technicalDetails, moreInfo, e);
    }

    // status 204
    public static ExceptionResponse createNoContentExceptionResponse() {

        return new ExceptionResponse(Response.Status.NO_CONTENT, EXCEPTION_TYPE_NO_CONTENT, null, null, null, null);
    }

    // status 204
    public static ExceptionResponse createNoContentExceptionResponse(Throwable e) {

        return new ExceptionResponse(Response.Status.NO_CONTENT, EXCEPTION_TYPE_NO_CONTENT, null, null, null, null, e);
    }

    // Business Exceptions

    // status 400
    public static ExceptionResponse createRequiredFieldExceptionResponse(String location) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_VALIDATION_FAILURE,
                EXCEPTION_MSG_RESPONSE_REQUIRED_FOR_FIELD, location, null, null);
    }

    // status 400
    public static ExceptionResponse createRequiredFieldExceptionResponse(String location, Throwable e) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_VALIDATION_FAILURE,
                EXCEPTION_MSG_RESPONSE_REQUIRED_FOR_FIELD, location, null, null, e);
    }

    // status 400
    public static ExceptionResponse createRequiredFieldExceptionResponse(String location, String moreInfo) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_VALIDATION_FAILURE,
                EXCEPTION_MSG_RESPONSE_REQUIRED_FOR_FIELD, location, null, moreInfo);
    }

    // status 400
    public static ExceptionResponse createRequiredFieldExceptionResponse(String location, String moreInfo,
            Throwable e) {

        return new ExceptionResponse(Response.Status.BAD_REQUEST, EXCEPTION_TYPE_VALIDATION_FAILURE,
                EXCEPTION_MSG_RESPONSE_REQUIRED_FOR_FIELD, location, null, moreInfo, e);
    }

    // status 404
    public static ExceptionResponse createRecordNotFoundExceptionResponse(String description) {

        return new ExceptionResponse(Response.Status.NOT_FOUND, EXCEPTION_TYPE_RECORD_NOT_FOUND, description, null,
                null, null);
    }

    // status 404
    public static ExceptionResponse createRecordNotFoundExceptionResponse(String description, Throwable e) {

        return new ExceptionResponse(Response.Status.NOT_FOUND, EXCEPTION_TYPE_RECORD_NOT_FOUND, description, null,
                null, null, e);
    }

    // status 404
    public static ExceptionResponse createRecordNotFoundExceptionResponse(String description, String technicalDetails) {

        return new ExceptionResponse(Response.Status.NOT_FOUND, EXCEPTION_TYPE_RECORD_NOT_FOUND, description, null,
                technicalDetails, null);
    }

    // status 404
    public static ExceptionResponse createRecordNotFoundExceptionResponse(String description, String technicalDetails,
            Throwable e) {

        return new ExceptionResponse(Response.Status.NOT_FOUND, EXCEPTION_TYPE_RECORD_NOT_FOUND, description, null,
                technicalDetails, null, e);
    }

    // status 404
    public static ExceptionResponse createRecordNotFoundExceptionResponse(String description, String technicalDetails,
            String moreInfo) {

        return new ExceptionResponse(Response.Status.NOT_FOUND, EXCEPTION_TYPE_RECORD_NOT_FOUND, description, null,
                technicalDetails, moreInfo);
    }

    // status 404
    public static ExceptionResponse createRecordNotFoundExceptionResponse(String description, String technicalDetails,
            String moreInfo, Throwable e) {

        return new ExceptionResponse(Response.Status.NOT_FOUND, EXCEPTION_TYPE_RECORD_NOT_FOUND, description, null,
                technicalDetails, moreInfo, e);
    }

}
