package com.doms.authentication;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.doms.authentication.dto.RequestEvent;
import com.doms.authentication.dto.ResponseEvent;
import com.doms.authentication.factory.DependencyFactory;
import com.doms.authentication.utils.DomsLogger;
import com.fasterxml.jackson.databind.ObjectMapper;

public class App implements RequestHandler<RequestEvent, ResponseEvent> {

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
    public ResponseEvent handleRequest(RequestEvent requestEvent,
                                       Context context) {
        DomsLogger.setLoggerApi(context);
        return ResponseEvent.builder().requestId(requestEvent.getRequestId()).build();
    }
}