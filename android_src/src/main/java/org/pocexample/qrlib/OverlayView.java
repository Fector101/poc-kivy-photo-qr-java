package org.pocexample.qrlib;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.View;

public class OverlayView extends View {
    private final Paint paint = new Paint();

    public OverlayView(Context context) {
        super(context);
        paint.setColor(Color.WHITE);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(6f);
        paint.setAntiAlias(true);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        int w = getWidth();
        int h = getHeight();
        int size = Math.min(w, h) * 3 / 5;
        int left = (w - size) / 2;
        int top = (h - size) / 2;
        canvas.drawRect(left, top, left + size, top + size, paint);
    }
}
