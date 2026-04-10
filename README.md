# poc-kivy-photo-qr-java
This project is a minimal Proof of Concept built with **Kivy**, **KivyMD 2.x dev**, and **Buildozer** for Android and shown a working photo&amp;qrcode decoder app done with python and kivy.
It use java as python&lt;->android bridge.


## What this POC does

The home screen contains only two actions:

1. **Take a photo**
2. **Scan a QR code**

A multiline log box is shown below the buttons. It is used to display what happens inside the app, for example:

- button pressed
- photo capture returned with file path
- QR scan returned with decoded value
- cancellation or errors

## Project structure

```text
poc-minimal/
├── android_src/
│   └── src/main/java/org/pocexample/
├── buildozer.spec
├── libs/
│   ├── constants.py
│   ├── objs.py
│   ├── qr_lib.py
│   └── utils.py
├── main.kv
├── main.py
└── README.md
```

## Main components

### `main.py`
Contains the main KivyMD application.

Responsibilities:
- initialize the app theme
- load the KV layout
- initialize the QR/camera helper
- handle button actions
- append messages to the multiline log box
- receive photo / QR scan callbacks

### `main.kv`
Defines the minimal UI:
- top app bar
- **Take a photo** button
- **Scan QR** button
- multiline log text box

### `libs/qr_lib.py`
Provides the bridge between Python and Android Java activities.

Responsibilities:
- request Android permissions
- start the Java activity for photo capture
- start the Java activity for QR scanning
- receive `on_activity_result`
- return the result to Python callbacks

### `android_src/...`
Contains the Android Java source code used by Buildozer.

Expected responsibilities:
- camera activity for image capture
- QR scan activity
- optional overlay views used by the Android camera UI


## Hooks and AndroidManifest fix

This project also includes a `libs/hooks/` directory.

These hooks are important because, in some Buildozer / python-for-android combinations, the generated Android project may not produce a fully correct `AndroidManifest.xml` for custom Java activities and related Android settings.

In practice, the hooks are used as a workaround for Buildozer / p4a manifest-generation issues.

### Why the hooks are needed

When packaging Android applications with custom Java code, Buildozer may generate a manifest that is incomplete or not fully aligned with the project requirements. Typical problems include:

- custom activities not correctly registered
- missing or incomplete manifest attributes
- package / activity name mismatches
- incorrect integration between Python side and Java side

Because of that, the app may build successfully but fail at runtime, or the custom camera / QR activities may not launch correctly.

### What the hooks do

The files under `libs/hooks/` are used during the Android build step to patch or adjust the generated Android project.

Their purpose is to make the packaged result consistent with the Java sources used by the app, especially when the default Buildozer-generated manifest is not enough.

In short, the hooks are there to:

- patch Buildozer / p4a Android build output
- fix manifest-related issues
- ensure custom Java activities are compiled and recognized correctly
- reduce packaging bugs caused by automatic manifest generation

### Why this matters in this POC

Even though this project is minimal, it still depends on custom Java activities for:

- photo capture
- QR scanning
- camera-related Android UI behavior

That means the Android package is not a pure Python-only application. Because of this, hooks remain useful as a defensive fix for Buildozer manifest-generation problems.

If you remove them, the build may still work in some environments, but it can also break depending on:

- Buildozer version
- python-for-android version
- Android API level
- local SDK / Gradle setup

So the hooks should be considered part of the Android packaging reliability layer.

## Android package name

The Java / Android package name is:

```text
org.pocexample
```

This replaces the original package name from the larger source project.

## Requirements

Main Python dependencies are defined in `buildozer.spec`.

Typical stack:
- Python 3
- Kivy
- KivyMD 2.x dev
- pyjnius
- Android bootstrap / python-for-android

Android side uses:
- CameraX
- ML Kit Barcode Scanning

## Build instructions

From the project root:

```bash
buildozer android debug
```

To clean previous Android builds:

```bash
buildozer android clean
buildozer android debug
```

## Notes

- This is a **POC**, not a production-ready application.
- The project is intentionally minimal and focuses only on the core Android integrations.
- Desktop execution can be used for UI testing, but photo and QR features are intended for **Android**.
- If permissions are denied, the Java activities may return cancellation or failure messages.

## Purpose

The purpose of this project is to provide a compact, easy-to-share example showing how to:

- call Android Java activities from a Kivy/KivyMD app
- capture a photo from Android camera code
- scan QR codes from Android camera code
- send results back to Python
- keep the user informed through a simple multiline log area
