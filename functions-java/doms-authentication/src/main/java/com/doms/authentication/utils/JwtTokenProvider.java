package com.doms.authentication.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Base64;
import java.util.Date;

public class JwtTokenProvider {

    private final String securityToken = "doms-services-key";

    private final long validityInMilliseconds = 60000; // 1 mins

    private final String secretKey;

    public JwtTokenProvider() {
        secretKey = Base64.getEncoder().encodeToString(securityToken.getBytes());
    }

    public String createToken(String userName) {
        Claims claims = Jwts.claims().setSubject(userName);
        Date now = new Date(System.currentTimeMillis());

        Date expiryDate = new Date(now.getTime() + validityInMilliseconds);
        return Jwts.builder().setClaims(claims).setIssuedAt(now).setExpiration(expiryDate)
                .signWith(SignatureAlgorithm.HS256, secretKey).compact();
    }

}
