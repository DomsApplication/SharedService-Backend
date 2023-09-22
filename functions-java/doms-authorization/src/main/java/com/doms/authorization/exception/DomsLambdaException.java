package com.doms.authorization.exception;

public class DomsLambdaException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    public DomsLambdaException() {
        this("");
    }

    public DomsLambdaException(String message) {
        super(message);
    }

    public DomsLambdaException(Throwable cause) {
        super(cause);
    }

    public DomsLambdaException(String message, Throwable cause) {
        super(message, cause);
    }

}