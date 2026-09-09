package com.myassist.customer.network;

import com.myassist.customer.BuildConfig;
import com.myassist.customer.session.SessionManager;
import java.util.concurrent.TimeUnit;
import okhttp3.OkHttpClient;
import okhttp3.Request;

public final class ApiClient {
    public static final String BASE_URL = BuildConfig.API_BASE_URL + "/";
    private static OkHttpClient client;
    private static SessionManager session;
    private ApiClient() {}
    public static void init(SessionManager sm) {
        session = sm;
        client = new OkHttpClient.Builder().connectTimeout(15, TimeUnit.SECONDS).readTimeout(20, TimeUnit.SECONDS)
            .addInterceptor(chain -> { Request original=chain.request(); Request.Builder b=original.newBuilder(); String token=session==null?null:session.token(); if(token!=null) b.header("Authorization","Bearer "+token); return chain.proceed(b.build()); }).build();
    }
    public static OkHttpClient http() { return client; }
    public static class ApiException extends Exception { public final int code; public final String userMessage; public ApiException(int c,String m){super(m);code=c;userMessage=m;} }
}