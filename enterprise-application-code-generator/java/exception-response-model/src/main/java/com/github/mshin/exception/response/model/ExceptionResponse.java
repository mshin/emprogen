package com.github.mshin.exception.response.model;

import java.io.Serializable;

import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

import io.swagger.annotations.ApiModelProperty;

/**
 * @author MunChul Shin
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "httpStatus",
    "type",
    "description",
    "location",
    "technicalDetails",
    "moreInfo"
})

@XmlRootElement(name = "ExceptionResponse")
@XmlAccessorType(XmlAccessType.NONE)
public class ExceptionResponse extends RuntimeException implements Serializable {

    private static final long serialVersionUID = -1937492209174401689L;

    @JsonProperty("httpStatus")
    @JsonPropertyDescription("The HTTP status type")
    @XmlElement
    @ApiModelProperty(required = true, value = "The HTTP status type", example = "200")
    private Response.Status httpStatus;

    @JsonProperty("type")
    @JsonPropertyDescription("Error type that describes the error.")
    @XmlElement
    @ApiModelProperty(required = true, value = "Error type that describes the error. Always returned to the caller.", example = "validationFailure OR invalidRequest OR serverError")
    private String type;

    @JsonProperty("description")
    @JsonPropertyDescription("Human readable description of the exception.")
    @XmlElement
    @ApiModelProperty(required = false, value = "Human readable description of the exception. If available, returned to the caller.", example = "Object doesn't exist.")
    private String description;

    @JsonProperty("location")
    @JsonPropertyDescription("Field that threw the exception (if field validation)")
    @XmlElement
    @ApiModelProperty(required = false, value = "Field that threw the exception (if field validation).", example = "userEmailTxtbox")
    private String location;

    @JsonProperty("technicalDetails")
    @JsonPropertyDescription("Technical details for exception.")
    @XmlElement
    @ApiModelProperty(required = false, value = "Technical details for exception. Not returned to non-technical end users.", example = "NullPointerException: userEmailTxtbox cannot be null.")
    private String technicalDetails;

    @JsonProperty("moreInfo")
    @JsonPropertyDescription("Extra information to be returned with the exception.")
    @XmlElement
    @ApiModelProperty(required = false, value = "Extra information to be returned with the exception. Can be exposed to end user or not.")
    private String moreInfo;

    public ExceptionResponse() {
        super();
    }

    public ExceptionResponse(Status httpStatus, String type) {
        super();
        this.httpStatus = httpStatus;
        this.type = type;
    }

    public ExceptionResponse(Status httpStatus, String type, Throwable e) {
        super(e);
        this.httpStatus = httpStatus;
        this.type = type;
    }

    public ExceptionResponse(Status httpStatus, String type, String description) {
        super();
        this.httpStatus = httpStatus;
        this.type = type;
        this.description = description;
    }

    public ExceptionResponse(Status httpStatus, String type, String description, Throwable e) {
        super(e);
        this.httpStatus = httpStatus;
        this.type = type;
        this.description = description;
    }

    public ExceptionResponse(Status httpStatus, String type, String description, String location) {
        super();
        this.httpStatus = httpStatus;
        this.type = type;
        this.description = description;
        this.location = location;
    }

    public ExceptionResponse(Status httpStatus, String type, String description, String location, Throwable e) {
        super(e);
        this.httpStatus = httpStatus;
        this.type = type;
        this.description = description;
        this.location = location;
    }

    public ExceptionResponse(Status httpStatus, String type, String description, String location,
            String technicalDetails, String moreInfo) {
        super();
        this.httpStatus = httpStatus;
        this.type = type;
        this.description = description;
        this.location = location;
        this.technicalDetails = technicalDetails;
        this.moreInfo = moreInfo;
    }

    public ExceptionResponse(Status httpStatus, String type, String description, String location,
            String technicalDetails, String moreInfo, Throwable e) {
        super(e);
        this.httpStatus = httpStatus;
        this.type = type;
        this.description = description;
        this.location = location;
        this.technicalDetails = technicalDetails;
        this.moreInfo = moreInfo;
    }

    public Response.Status getHttpStatus() {
        return httpStatus;
    }

    public void setHttpStatus(Response.Status httpStatus) {
        this.httpStatus = httpStatus;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getTechnicalDetails() {
        return technicalDetails;
    }

    public void setTechnicalDetails(String technicalDetails) {
        this.technicalDetails = technicalDetails;
    }

    public String getMoreInfo() {
        return moreInfo;
    }

    public void setMoreInfo(String moreInfo) {
        this.moreInfo = moreInfo;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((description == null) ? 0 : description.hashCode());
        result = prime * result + ((httpStatus == null) ? 0 : httpStatus.hashCode());
        result = prime * result + ((location == null) ? 0 : location.hashCode());
        result = prime * result + ((moreInfo == null) ? 0 : moreInfo.hashCode());
        result = prime * result + ((technicalDetails == null) ? 0 : technicalDetails.hashCode());
        result = prime * result + ((type == null) ? 0 : type.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        ExceptionResponse other = (ExceptionResponse) obj;
        if (description == null) {
            if (other.description != null)
                return false;
        } else if (!description.equals(other.description))
            return false;
        if (httpStatus != other.httpStatus)
            return false;
        if (location == null) {
            if (other.location != null)
                return false;
        } else if (!location.equals(other.location))
            return false;
        if (moreInfo == null) {
            if (other.moreInfo != null)
                return false;
        } else if (!moreInfo.equals(other.moreInfo))
            return false;
        if (technicalDetails == null) {
            if (other.technicalDetails != null)
                return false;
        } else if (!technicalDetails.equals(other.technicalDetails))
            return false;
        if (type == null) {
            if (other.type != null)
                return false;
        } else if (!type.equals(other.type))
            return false;
        return true;
    }

    @Override
    public String toString() {
        return "ExceptionResponse [httpStatus=" + httpStatus + ", type=" + type + ", description=" + description
                + ", location=" + location + ", technicalDetails=" + technicalDetails + ", moreInfo=" + moreInfo + "]";
    }

}
