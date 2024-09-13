package com.github.mshin.jaxrms.rs.api.model;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;

import io.swagger.annotations.ApiModelProperty;

/**
 * @author MunChul Shin
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@XmlAccessorType(XmlAccessType.FIELD)
@XmlRootElement(name = "GetGreetingResponse")
public class GetGreetingResponse {

    @JsonProperty("greeting")
    @JsonPropertyDescription("The greeting.")
    @XmlElement
    @ApiModelProperty(value = "The greeting.")
    private String greeting;
    
    @JsonProperty("responseCode")
    @JsonPropertyDescription("0 is success, otherwise failure.")
    @XmlElement
    @ApiModelProperty(value = "0 is success, otherwise failure.")
    private Integer responseCode;

    public GetGreetingResponse() {
    }

    public GetGreetingResponse(String greeting, Integer responseCode) {
        super();
        this.greeting = greeting;
        this.responseCode = responseCode;
    }

    public String getGreeting() {
        return greeting;
    }

    public void setGreeting(String greeting) {
        this.greeting = greeting;
    }

    public Integer getResponseCode() {
        return responseCode;
    }

    public void setResponseCode(Integer responseCode) {
        this.responseCode = responseCode;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((greeting == null) ? 0 : greeting.hashCode());
        result = prime * result + ((responseCode == null) ? 0 : responseCode.hashCode());
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
        GetGreetingResponse other = (GetGreetingResponse) obj;
        if (greeting == null) {
            if (other.greeting != null)
                return false;
        } else if (!greeting.equals(other.greeting))
            return false;
        if (responseCode == null) {
            if (other.responseCode != null)
                return false;
        } else if (!responseCode.equals(other.responseCode))
            return false;
        return true;
    }

    @Override
    public String toString() {
        return "GetGreetingResponse [greeting=" + greeting + ", responseCode=" + responseCode + "]";
    }
    
    
}
