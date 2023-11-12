package com.doms.authentication;

import com.amazonaws.HttpMethod;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.doms.authentication.dto.ResponseEvent;
import com.doms.authentication.exception.DomsLambdaException;
import com.doms.authentication.factory.DependencyFactory;
import com.doms.authentication.handler.Service;
import com.doms.authentication.utils.DomsLogger;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import software.amazon.awssdk.http.HttpStatusCode;

public class App implements RequestHandler<APIGatewayProxyRequestEvent, ResponseEvent> {

    private final ObjectMapper objectMapper;

    private final Service service;

    /**
     * This is the main constructor for real working.
     */
    public App() {
        objectMapper = DependencyFactory.objectMapperInstance();
        service = new Service();
    }

    /**
     * This is the test constructor should only be used in test environment.
     *
     * @param objectMapper
     */
    App(ObjectMapper objectMapper, Service service) {
        this.objectMapper = objectMapper;
        this.service = service;
    }


    @Override
    public ResponseEvent handleRequest(APIGatewayProxyRequestEvent proxyRequestEvent, Context context) {
        DomsLogger.setLoggerApi(context);
        ResponseEvent responseEvent = null;
        try {
            if (proxyRequestEvent.getPath().equals("/auth/token")
                    && proxyRequestEvent.getHttpMethod().equals(HttpMethod.POST.toString())) {
                responseEvent = this.service.getToken(proxyRequestEvent.getBody(), objectMapper);

            } else if (proxyRequestEvent.getPath().equals("/auth/info")
                    && proxyRequestEvent.getHttpMethod().equals(HttpMethod.GET.toString())) {
                responseEvent = this.service.getServiceInfo(context, objectMapper);

            } else {
                responseEvent = ResponseEvent.builder().statusCode(HttpStatusCode.BAD_REQUEST)
                        .body("Invalid request : " + proxyRequestEvent.getPath()).build();
            }
        } catch (JsonProcessingException | DomsLambdaException e) {
            DomsLogger.log("EXCEPTION in MAIN HANDLER", e);
            responseEvent = ResponseEvent.builder().statusCode(HttpStatusCode.INTERNAL_SERVER_ERROR)
                    .body(e.getLocalizedMessage()).build();
        }
        return responseEvent;
    }
}