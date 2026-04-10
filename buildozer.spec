[app]
title = POC Example
package.name = pocexample
package.domain = org.pocexample
source.dir = .
source.include_exts = py,kv,java
source.include_patterns = ./*.kv

requirements = python3,
    kivy==2.3.1,
    https://github.com/kivymd/KivyMD/archive/master.zip,
    materialyoucolor,
    asynckivy,
    asyncgui,
    pillow,
    android,
    pyjnius,
    filetype

version = 0.1

android.permissions = android.permission.CAMERA, android.permission.VIBRATE
android.api = 34
android.minapi = 26
android.enable_androidx = True
android.archs = arm64-v8a
android.add_src = android_src/src/main/java
android.gradle_dependencies = androidx.camera:camera-core:1.3.4,androidx.camera:camera-camera2:1.3.4,androidx.camera:camera-lifecycle:1.3.4,androidx.camera:camera-view:1.3.4,com.google.mlkit:barcode-scanning:17.3.0,org.jetbrains.kotlin:kotlin-stdlib:1.8.22,org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.8.22,org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.8.22,androidx.appcompat:appcompat:1.6.1,androidx.activity:activity:1.8.2
android.gradle_repositories = google(), mavenCentral()


p4a.hook = libs/hooks/hooks.py

orientation = portrait, landscape, portrait-reverse, landscape-reverse
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
