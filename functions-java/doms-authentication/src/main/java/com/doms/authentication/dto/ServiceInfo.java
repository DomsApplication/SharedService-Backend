package com.doms.authentication.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@Data
@AllArgsConstructor
@NoArgsConstructor
@SuperBuilder
@JsonIgnoreProperties(ignoreUnknown = true)
public class ServiceInfo {

    private String serviceName;

    private String awsRequestId;

    private String funcationName;

    private String funcationVersion;

    private String timestamp;

    private int memoryLimit;
}
