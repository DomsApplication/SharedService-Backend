package com.doms.authentication.dto;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.List;
import java.util.Map;

@Data
@AllArgsConstructor
@NoArgsConstructor
@SuperBuilder
@JsonIgnoreProperties(ignoreUnknown = true)
public class ResponseEvent {

    private static final long serialVersionUID = 2263167344670024172L;
    private Integer statusCode;
    private Map<String, String> headers;
    private Map<String, List<String>> multiValueHeaders;
    private String body;
    private Boolean isBase64Encoded;

    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        if (this.getStatusCode() != null) {
            sb.append("statusCode: ").append(this.getStatusCode()).append(",");
        }

        if (this.getHeaders() != null) {
            sb.append("headers: ").append(this.getHeaders().toString()).append(",");
        }

        if (this.getMultiValueHeaders() != null) {
            sb.append("multiValueHeaders: ").append(this.getMultiValueHeaders().toString()).append(",");
        }

        if (this.getBody() != null) {
            sb.append("body: ").append(this.getBody());
        }

        sb.append("}");
        return sb.toString();
    }

    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        } else if (obj == null) {
            return false;
        } else if (!(obj instanceof APIGatewayProxyResponseEvent)) {
            return false;
        } else {
            APIGatewayProxyResponseEvent other = (APIGatewayProxyResponseEvent) obj;
            if (other.getStatusCode() == null ^ this.getStatusCode() == null) {
                return false;
            } else if (other.getStatusCode() != null && !other.getStatusCode().equals(this.getStatusCode())) {
                return false;
            } else if (other.getHeaders() == null ^ this.getHeaders() == null) {
                return false;
            } else if (other.getHeaders() != null && !other.getHeaders().equals(this.getHeaders())) {
                return false;
            } else if (other.getMultiValueHeaders() == null ^ this.getMultiValueHeaders() == null) {
                return false;
            } else if (other.getMultiValueHeaders() != null && !other.getMultiValueHeaders()
                    .equals(this.getMultiValueHeaders())) {
                return false;
            } else if (other.getBody() == null ^ this.getBody() == null) {
                return false;
            } else {
                return other.getBody() == null || other.getBody().equals(this.getBody());
            }
        }
    }

    public int hashCode() {
        int hashCode = 1;
        hashCode = 31 * hashCode + (this.getStatusCode() == null ? 0 : this.getStatusCode().hashCode());
        hashCode = 31 * hashCode + (this.getHeaders() == null ? 0 : this.getHeaders().hashCode());
        hashCode = 31 * hashCode + (this.getMultiValueHeaders() == null ? 0 : this.getMultiValueHeaders().hashCode());
        hashCode = 31 * hashCode + (this.getBody() == null ? 0 : this.getBody().hashCode());
        return hashCode;
    }

}
