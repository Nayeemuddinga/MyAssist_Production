package com.myassist.customer.network;

import org.json.JSONObject;
import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public final class ApiService {
    private static final MediaType JSON=MediaType.get("application/json; charset=utf-8");
    public interface Parser<T>{ T parse(JSONObject body)throws Exception; }
    public interface Callback<T>{ void onSuccess(T value); void onError(ApiClient.ApiException e); }
    public static <T> void run(Request req, Parser<T> parser, Callback<T> cb){ new Thread(()->{try(Response r=ApiClient.http().newCall(req).execute()){String raw=r.body()==null?"":r.body().string(); JSONObject body=raw.isEmpty()?new JSONObject():new JSONObject(raw); if(!r.isSuccessful()){String msg=body.optJSONObject("error")==null?null:body.optJSONObject("error").optString("message",null); if(msg==null) msg=r.code()==401?"Session expired. Please log in again.":r.code()==409?"Conflict — the item has changed.":"Request failed."; cb.onError(new ApiClient.ApiException(r.code(),msg));return;} cb.onSuccess(parser.parse(body));}catch(Exception e){cb.onError(new ApiClient.ApiException(0,"No internet connection. Check your network and try again."));}}).start(); }
    public static Request get(String path){return new Request.Builder().url(ApiClient.BASE_URL+path).get().build();}
    public static Request post(String path,JSONObject json){return new Request.Builder().url(ApiClient.BASE_URL+path).post(RequestBody.create(json.toString(),JSON)).build();}
}