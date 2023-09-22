package com.doms.authentication;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.doms.authentication.factory.DependencyFactory;
import com.doms.authentication.utils.DomsLogger;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

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
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent proxyRequestEvent, Context context) {
        DomsLogger.setLoggerApi(context);
        APIGatewayProxyResponseEvent apiGatewayProxyResponseEvent = new APIGatewayProxyResponseEvent();
        try {
            DomsLogger.log("HTTP METHOD:::", proxyRequestEvent.getHttpMethod());
            DomsLogger.log("PATH:::", proxyRequestEvent.getPath());
            DomsLogger.log("PATH PARAMETERS:::", proxyRequestEvent.getPathParameters().toString());
            DomsLogger.log("QUERY PARAMETERS:::", proxyRequestEvent.getQueryStringParameters().toString());
            DomsLogger.log("HEADERS:::", proxyRequestEvent.getHeaders().toString());
            DomsLogger.log("VERSION:::", proxyRequestEvent.getVersion());

            String requestString = proxyRequestEvent.getBody();
            JSONParser parser = new JSONParser();
            JSONObject requestJsonObject = (JSONObject) parser.parse(requestString);
            String requestMessage = null;
            String responseMessage = null;
            if (requestJsonObject != null) {
                if (requestJsonObject.get("requestMessage") != null) {
                    requestMessage = requestJsonObject.get("requestMessage").toString();
                }
            }

            Map<String, String> responseBody = new HashMap<String, String>();
            responseBody.put("responseMessage", requestMessage);
            responseMessage = new JSONObject(responseBody).toJSONString();

            apiGatewayProxyResponseEvent.setHeaders(
                    Collections.singletonMap("timeStamp", String.valueOf(System.currentTimeMillis())));
            apiGatewayProxyResponseEvent.setStatusCode(200);
            apiGatewayProxyResponseEvent.setBody(requestMessage);
            return apiGatewayProxyResponseEvent;
        } catch (ParseException e) {
            e.printStackTrace();
            apiGatewayProxyResponseEvent.setStatusCode(200);
            apiGatewayProxyResponseEvent.setBody(e.getLocalizedMessage());
            return apiGatewayProxyResponseEvent;
        }
    }
}