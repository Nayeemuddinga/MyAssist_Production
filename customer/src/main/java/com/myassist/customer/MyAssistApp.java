package com.myassist.customer;

import android.app.Application;
import com.myassist.customer.session.SessionManager;

public class MyAssistApp extends Application {
    private static MyAssistApp instance;
    private SessionManager session;
    @Override public void onCreate() {
        super.onCreate();
        instance = this;
        session = new SessionManager(this);
    }
    public static MyAssistApp getInstance() { return instance; }
    public SessionManager session() { return session; }
}
