package com.doms.authorization.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@Data
@AllArgsConstructor
@NoArgsConstructor
@SuperBuilder
@JsonIgnoreProperties(ignoreUnknown = true)
public class TokenAuthorizerContext {

    @JsonProperty("type")
    private String type;

    @JsonProperty("authorizationToken")
    private String authorizationToken;

    @JsonProperty("methodArn")
    private String methodArn;

}
