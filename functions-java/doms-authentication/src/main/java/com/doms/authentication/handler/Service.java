package com.doms.authentication.handler;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.util.StringUtils;
import com.doms.authentication.dto.LoginRequest;
import com.doms.authentication.dto.ResponseEvent;
import com.doms.authentication.dto.ServiceInfo;
import com.doms.authentication.exception.DomsLambdaException;
import com.doms.authentication.utils.JwtTokenProvider;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import software.amazon.awssdk.http.HttpStatusCode;

import java.time.ZonedDateTime;
import java.util.TimeZone;

public class Service {

    public ResponseEvent getServiceInfo(Context context, ObjectMapper objectMapper) throws JsonProcessingException {
        ServiceInfo info = new ServiceInfo();
        info.setAwsRequestId(context.getAwsRequestId());
        info.setFuncationName(context.getFunctionName());
        info.setFuncationVersion(context.getFunctionVersion());
        info.setServiceName(context.getFunctionName());
        ZonedDateTime zoneNow = ZonedDateTime.now(TimeZone.getTimeZone("Europe/Madrid").toZoneId());
        info.setTimestamp(zoneNow.toString());

        return ResponseEvent.builder()
                .statusCode(HttpStatusCode.OK)
                .body(objectMapper.writeValueAsString(info))
                .build();
    }

    public ResponseEvent getToken(String payload, ObjectMapper objectMapper) throws DomsLambdaException {
        if (StringUtils.isNullOrEmpty(payload)) {
            return ResponseEvent.builder()
                    .statusCode(HttpStatusCode.NOT_ACCEPTABLE)
                    .body("No request Body.")
                    .build();
        }
        try {
            LoginRequest loginRequest = objectMapper.convertValue(payload, LoginRequest.class);
            if (loginRequest.getUsername().equals("ADMIN")) {
                ObjectNode objectNode = objectMapper.createObjectNode();
                objectNode.put("username", loginRequest.getUsername());
                objectNode.put("access-token", new JwtTokenProvider().createToken(loginRequest.getUsername()));
                return ResponseEvent.builder()
                        .statusCode(HttpStatusCode.OK)
                        .body(objectNode.toString())
                        .build();
            } else {
                return ResponseEvent.builder()
                        .statusCode(HttpStatusCode.UNAUTHORIZED)
                        .body("The user " + loginRequest.getUsername() + " not exists.")
                        .build();
            }
        } catch (IllegalArgumentException e) {
            return ResponseEvent.builder()
                    .statusCode(HttpStatusCode.BAD_REQUEST)
                    .body("Invalid request Body.")
                    .build();
        }
    }
}
