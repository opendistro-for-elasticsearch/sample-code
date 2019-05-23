// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.io.Encoders;
import io.jsonwebtoken.security.Keys;
import java.security.Key;
import java.util.Date;
import java.util.HashMap;

public class JWTTestTokens {
    public static void main(String[] args) {
        Key key = Keys.secretKeyFor(SignatureAlgorithm.HS256);
        Date exp = new Date(System.currentTimeMillis() + 1000000);
        HashMap<String,Object> hm = new HashMap<>();
        hm.put("roles","admin");
        String jws = Jwts.builder()
                .setClaims(hm)
                .setIssuer("https://localhost")
                .setSubject("admin")
                .setExpiration(exp)
                .signWith(key).compact();
        System.out.println("Token:");
        System.out.println(jws);
        if(Jwts.parser().setSigningKey(key).parseClaimsJws(jws).getBody().getSubject().equals("test")) {
            System.out.println("test");
        }
        String encoded = Encoders.BASE64.encode(key.getEncoded());
        System.out.println("Shared secret:");
        System.out.println(encoded);
    }
}
