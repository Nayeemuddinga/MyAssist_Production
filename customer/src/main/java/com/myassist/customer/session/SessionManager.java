package com.myassist.customer.session;

import android.content.Context;
import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKey;

public class SessionManager {
    private static final String PREFS = "myassist_secure_session";
    private final android.content.SharedPreferences prefs;

    public SessionManager(Context ctx) {
        try {
            MasterKey key = new MasterKey.Builder(ctx).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build();
            prefs = new EncryptedSharedPreferences.Builder(ctx, PREFS, key,
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM).build();
        } catch (Exception e) {
            throw new IllegalStateException("Secure storage unavailable", e);
        }
    }

    public void save(String token, int userId, String role, String fullName) {
        prefs.edit().putString("token", token).putInt("user_id", userId)
                .putString("role", role).putString("full_name", fullName).apply();
    }
    public String token() { return prefs.getString("token", null); }
    public int userId() { return prefs.getInt("user_id", -1); }
    public String fullName() { return prefs.getString("full_name", ""); }
    public String role() { return prefs.getString("role", ""); }
    public boolean isLoggedIn() { return token() != null; }
    public void clear() { prefs.edit().clear().apply(); }
}
