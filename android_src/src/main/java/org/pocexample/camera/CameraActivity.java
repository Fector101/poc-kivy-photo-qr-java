package org.pocexample.camera;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.content.res.ColorStateList;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.activity.ComponentActivity;
import androidx.camera.core.Camera;
import androidx.camera.core.CameraControl;
import androidx.camera.core.CameraInfo;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Locale;
import java.util.concurrent.Executor;

public class CameraActivity extends ComponentActivity {

    public static final String EXTRA_PHOTO_PATH = "photo_path";
    private static final int REQ_CAMERA = 10;

    private PreviewView previewView;
    private ImageCapture imageCapture;
    private ProcessCameraProvider cameraProvider;
    private Executor mainExecutor;

    private Camera camera;
    private CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

    private boolean torchOn = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        mainExecutor = ContextCompat.getMainExecutor(this);

        // ===== ROOT =====
        FrameLayout root = new FrameLayout(this);

        // ===== PREVIEW =====
        previewView = new PreviewView(this);
        previewView.setLayoutParams(new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        ));
        // default CameraX is FILL_CENTER; ok for most camera apps :contentReference[oaicite:1]{index=1}
        previewView.setScaleType(PreviewView.ScaleType.FILL_CENTER);
        root.addView(previewView);

        // ===== BOTTOM BAR =====
        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER);
        bar.setPadding(dp(18), dp(12), dp(18), dp(24));

        FrameLayout.LayoutParams barParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        barParams.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
        bar.setLayoutParams(barParams);

        // sfondo “vetro scuro” (semplice)
        GradientDrawable barBg = new GradientDrawable();
        barBg.setColor(Color.parseColor("#66000000"));
        barBg.setCornerRadius(dp(28));
        bar.setBackground(barBg);

        // ===== BUTTONS =====
        ImageButton btnFlip = makeRoundIconButton(android.R.drawable.ic_menu_rotate, dp(44));
        ImageButton btnShoot = makeRoundIconButton(android.R.drawable.ic_menu_camera, dp(72)); // “scatta”
        ImageButton btnTorch = makeRoundIconButton(android.R.drawable.btn_star_big_off, dp(44));

        LinearLayout.LayoutParams smallLp = new LinearLayout.LayoutParams(dp(48), dp(48));
        smallLp.leftMargin = dp(10);
        smallLp.rightMargin = dp(10);

        LinearLayout.LayoutParams bigLp = new LinearLayout.LayoutParams(dp(76), dp(76));
        bigLp.leftMargin = dp(14);
        bigLp.rightMargin = dp(14);

        bar.addView(btnFlip, smallLp);
        bar.addView(btnShoot, bigLp);
        bar.addView(btnTorch, smallLp);

        root.addView(bar);

        // ===== CLOSE (top-left) =====
        ImageButton btnClose = makeRoundIconButton(android.R.drawable.ic_menu_close_clear_cancel, dp(40));
        FrameLayout.LayoutParams closeLp = new FrameLayout.LayoutParams(dp(44), dp(44));
        closeLp.gravity = Gravity.TOP | Gravity.START;
        closeLp.leftMargin = dp(12);
        closeLp.topMargin = dp(12);
        root.addView(btnClose, closeLp);

        setContentView(root);

        // ===== HANDLERS =====
        btnClose.setOnClickListener(v -> { setResult(RESULT_CANCELED); finish(); });

        btnShoot.setOnClickListener(v -> takePhoto());

        btnFlip.setOnClickListener(v -> {
            cameraSelector = (cameraSelector == CameraSelector.DEFAULT_BACK_CAMERA)
                    ? CameraSelector.DEFAULT_FRONT_CAMERA
                    : CameraSelector.DEFAULT_BACK_CAMERA;
            bindCameraUseCases();
        });

        btnTorch.setOnClickListener(v -> toggleTorch(btnTorch));

        // ===== PERMISSION =====
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                == PackageManager.PERMISSION_GRANTED) {
            startCamera();
        } else {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA},
                    REQ_CAMERA);
        }
    }

    // ---------- CameraX ----------
    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> future =
                ProcessCameraProvider.getInstance(this);

        future.addListener(() -> {
            try {
                cameraProvider = future.get();
                bindCameraUseCases();
            } catch (Exception e) {
                Toast.makeText(this, "Error CameraProvider: " + e.getMessage(),
                        Toast.LENGTH_LONG).show();
                setResult(RESULT_CANCELED);
                finish();
            }
        }, mainExecutor);
    }

    private void bindCameraUseCases() {
        if (cameraProvider == null) return;

        cameraProvider.unbindAll();

        Preview preview = new Preview.Builder().build();
        preview.setSurfaceProvider(previewView.getSurfaceProvider());

        imageCapture = new ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build();

        try {
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture);
            applyTorchState(null);
        } catch (Exception e) {
            Toast.makeText(this, "Bind failed: " + e.getMessage(),
                    Toast.LENGTH_LONG).show();
        }
    }

    private void takePhoto() {
        if (imageCapture == null) return;

        File dir = new File(getCacheDir(), "captures");
        if (!dir.exists()) dir.mkdirs();

        String ts = new SimpleDateFormat("yyyyMMdd_HHmmss_SSS", Locale.US)
                .format(System.currentTimeMillis());
        File file = new File(dir, "IMG_" + ts + ".jpg");

        ImageCapture.OutputFileOptions options =
                new ImageCapture.OutputFileOptions.Builder(file).build();

        imageCapture.takePicture(options, mainExecutor, new ImageCapture.OnImageSavedCallback() {
            @Override
            public void onImageSaved(@NonNull ImageCapture.OutputFileResults output) {
                Intent data = new Intent();
                data.putExtra(EXTRA_PHOTO_PATH, file.getAbsolutePath());
                setResult(RESULT_OK, data);
                finish();
            }

            @Override
            public void onError(@NonNull ImageCaptureException exception) {
                Toast.makeText(CameraActivity.this,
                        "Error: " + exception.getMessage(),
                        Toast.LENGTH_LONG).show();
            }
        });
    }

    // ---------- Torch ----------
    private void toggleTorch(ImageButton btnTorch) {
        torchOn = !torchOn;
        applyTorchState(btnTorch);
    }

    private void applyTorchState(ImageButton btnTorch) {
        if (camera == null) return;

        CameraInfo info = camera.getCameraInfo();
        CameraControl control = camera.getCameraControl();

        if (!info.hasFlashUnit()) {
            torchOn = false;
            Toast.makeText(this, "Torch not available", Toast.LENGTH_SHORT).show();
            return;
        }

        control.enableTorch(torchOn);

        // cambia iconcina (semplice)
        if (btnTorch != null) {
            btnTorch.setImageResource(torchOn
                    ? android.R.drawable.btn_star_big_on
                    : android.R.drawable.btn_star_big_off);
        }
    }

    // ---------- Helpers UI ----------
    private ImageButton makeRoundIconButton(int iconRes, int sizePx) {
        ImageButton b = new ImageButton(this);
        b.setScaleType(ImageButton.ScaleType.CENTER_INSIDE);
        b.setImageResource(iconRes);
        b.setPadding(dp(10), dp(10), dp(10), dp(10));
        b.setBackground(makeRoundRippleBackground());
        b.setColorFilter(Color.WHITE);

        // shadow/elevation (fa già molto “meno brutto”)
        b.setElevation(dp(4));

        // dimensione
        b.setLayoutParams(new ViewGroup.LayoutParams(sizePx, sizePx));
        return b;
    }

    private Drawable makeRoundRippleBackground() {
        // cerchio scuro
        GradientDrawable circle = new GradientDrawable();
        circle.setShape(GradientDrawable.OVAL);
        circle.setColor(Color.parseColor("#66000000"));

        // ripple chiaro
        RippleDrawable ripple = new RippleDrawable(
                ColorStateList.valueOf(Color.parseColor("#55FFFFFF")),
                circle,
                null
        );
        return ripple;
    }

    private int dp(int dp) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                dp,
                getResources().getDisplayMetrics()
        );
    }

    // ---------- Permission ----------
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == REQ_CAMERA) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startCamera();
            } else {
                Toast.makeText(this, "No permits", Toast.LENGTH_LONG).show();
                setResult(RESULT_CANCELED);
                finish();
            }
        }
    }
}
