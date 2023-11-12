export const handler = async (event, context) => {
    console.log('authorization REQUEST::' + JSON.stringify(event, undefined, 2));

    console.log('RemainingTime::' + context.getRemainingTimeInMillis());
    console.log('functionName::' + context.functionName);
    console.log('context::' + JSON.stringify(context));

    const token = event.authorizationToken;
    const methodArn = event.methodArn;

    switch(token) {
        case 'allow' :
            return generateAuthResponse('user', 'Allow', methodArn);
        default:
            return generateAuthResponse('user', 'Deny', methodArn);
    }
};

function generateAuthResponse(principalId, effect, methodArn) {
    const policyDocument = generatepolicyDocument(effect, methodArn);
    return {
        "principalId": principalId,
        "policyDocument": policyDocument
    }
}

function generatepolicyDocument(effect, methodArn) {
    if(!effect || !methodArn) return null;
    const policyDocument = {
        Version: '2012-10-17',
        Statement: [{
            "Action": "execute-api:Invoke",
            "Effect": effect,
            "Resource": methodArn
        }]
    };
    return policyDocument;
}
