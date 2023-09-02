package com.doms.platform;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.doms.platform.factory.DependencyFactory;
import com.doms.platform.utils.DomsLogger;
import com.fasterxml.jackson.databind.ObjectMapper;

public class App implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    private final ObjectMapper objectMapper;

    /**
     * This is the main constructor for real working.
     */
    public App() {
        objectMapper = DependencyFactory.objectMapperInstance();
    }

    /**
     * This is the test constructor should only be used in test environment.
     *
     * @param objectMapper
     */
    App(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }


    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent apiGatewayProxyRequestEvent,
                                                      Context context) {
        DomsLogger.setLoggerApi(context);
        return new APIGatewayProxyResponseEvent().withBody(apiGatewayProxyRequestEvent.getBody());
    }
}