package com.myassist.assistant.ui;

import android.os.Handler;
import android.os.Looper;

public abstract class UiCallback<T> {
    private final Handler handler = new Handler(Looper.getMainLooper());
    public final void success(T value) { handler.post(() -> onSuccess(value)); }
    public final void failure(Exception error) { handler.post(() -> onError(error)); }
    public abstract void onSuccess(T value);
    public abstract void onError(Exception error);
}
