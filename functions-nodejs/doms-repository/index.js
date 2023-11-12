export const handler = async (event, context) => {
    console.log('Repository REQUEST::' + JSON.stringify(event, undefined, 2));

    console.log('RemainingTime::' + context.getRemainingTimeInMillis());
    console.log('functionName::' + context.functionName);
    console.log('context::' + JSON.stringify(context));

    let responseCode = 200;

    let responseBody = {
        'lambda type' : 'repository',
        input: event
    };

    // The output from a Lambda proxy integration must be 
    // in the following JSON object. The 'headers' property 
    // is for custom response headers in addition to standard 
    // ones. The 'body' property  must be a JSON string. For 
    // base64-encoded payload, you must also set the 'isBase64Encoded'
    // property to 'true'.
    let response = {
        statusCode: responseCode,
        headers: {
            "x-custom-header" : "my custom header value"
        },
        body: JSON.stringify(responseBody)
    };
    console.log("response: " + JSON.stringify(response))
    return response;
};

