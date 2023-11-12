package com.doms.platform.utils;


import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class DomsLogger {

    private static final String LOGGER_MESSAGE = "{%s} : %s";
    private static LambdaLogger logger;
    private static String requestId = "********-****-****-****-************";

    public static void setLoggerApi(Context context) {
        logger = context.getLogger();
        requestId = (null != context.getAwsRequestId()) ? context.getAwsRequestId() : requestId;
    }

    public static void log(String message) {
        logApi(String.format(LOGGER_MESSAGE, requestId, message));
    }

    public static void log(String message, String value) {
        log(message + " ::: " + value);
    }

    public static void log(String message, Exception e) {
        log(message + " ::: " + e.getLocalizedMessage());
    }

    public static void log(Exception e) {
        log("", e);
    }

    private static void logApi(String log) {
        if (null != logger) {
            logger.log(log + "\n");
        } else {
            System.out.println(log);
        }
    }
}
