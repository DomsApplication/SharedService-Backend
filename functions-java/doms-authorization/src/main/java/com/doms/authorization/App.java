package com.doms.authorization;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.util.StringUtils;
import com.doms.authorization.dto.TokenAuthorizerContext;
import com.doms.authorization.exception.DomsLambdaException;
import com.doms.authorization.factory.DependencyFactory;
import com.doms.authorization.utils.DomsLogger;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class App implements RequestHandler<TokenAuthorizerContext, String> {

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
    public String handleRequest(TokenAuthorizerContext tokenContext, Context context) {
        DomsLogger.setLoggerApi(context);
        try {
            DomsLogger.log("Authorization", "............");
            String token = tokenContext.getAuthorizationToken();
            String methodArn = tokenContext.getMethodArn();
            DomsLogger.log("TOKEN", token);
            DomsLogger.log("METHOD ARN", methodArn);

            return this.generateAuthResponse("ADMIN", "Allow", methodArn);
        } catch (JsonProcessingException | DomsLambdaException e) {
            DomsLogger.log("EXCEPTION in MAIN HANDLER", e);
        }
        return null;
    }

    private String generateAuthResponse(String principalId, String effect, String methodArn)
            throws JsonProcessingException {
        ObjectNode policyNode = objectMapper.createObjectNode();
        policyNode.put("principalId", principalId);
        policyNode.put("policyDocument", this.generatepolicyDocument(effect, methodArn));
        String policyJson = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(policyNode);
        DomsLogger.log("policyJson", policyJson);
        return policyJson;
    }

    private ObjectNode generatepolicyDocument(String effect, String methodArn) {
        if (StringUtils.isNullOrEmpty(effect) || StringUtils.isNullOrEmpty(methodArn)) {
            return null;
        }
        ObjectNode statementNode = objectMapper.createObjectNode();
        statementNode.put("Action", "execute-api:Invoke");
        statementNode.put("Effect", effect);
        statementNode.put("Resource", methodArn);

        ArrayNode statementArray = objectMapper.createArrayNode();
        statementArray.add(statementNode);

        ObjectNode policyDocument = objectMapper.createObjectNode();
        policyDocument.put("Version", "2012-10-17");
        policyDocument.put("Statement", statementArray);
        return policyDocument;
    }

}