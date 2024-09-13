package com.github.mshin.exception.response.model;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementWrapper;
import javax.xml.bind.annotation.XmlRootElement;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;

import io.swagger.annotations.ApiModelProperty;

/**
 * @author MunChul Shin
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@XmlRootElement(name = "ExceptionResponses")
@XmlAccessorType(XmlAccessType.NONE)
public class ExceptionResponses extends RuntimeException implements Serializable {

    private static final long serialVersionUID = -1038061992638912110L;

    @JsonProperty("exceptionResponses")
    @JsonPropertyDescription("A list containing 0 or more ExceptionResponse Objects.")
    @XmlElementWrapper(name = "exceptionResponses")
    @XmlElement
    @ApiModelProperty(required = true, value = "A list containing 0 or more ExceptionResponse Objects.")
    private List<ExceptionResponse> exceptionResponses = new ArrayList<>();

    public ExceptionResponses() {
        super();
    }

    public ExceptionResponses(ExceptionResponse exceptionResponse) {
        super();
        exceptionResponses.add(exceptionResponse);
    }

    public ExceptionResponses(List<ExceptionResponse> exceptionResponses) {
        super();
        this.exceptionResponses = exceptionResponses;
    }

    public List<ExceptionResponse> getExceptionResponses() {
        return exceptionResponses;
    }

    public void setExceptionResponses(List<ExceptionResponse> exceptionResponses) {
        this.exceptionResponses = exceptionResponses;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((exceptionResponses == null) ? 0 : exceptionResponses.hashCode());
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
        ExceptionResponses other = (ExceptionResponses) obj;
        if (exceptionResponses == null) {
            if (other.exceptionResponses != null)
                return false;
        } else if (!exceptionResponses.equals(other.exceptionResponses))
            return false;
        return true;
    }

    @Override
    public String toString() {
        return "ExceptionResponses [exceptionResponses=" + exceptionResponses + "]";
    }

}
