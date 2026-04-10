JAVA_IDENT = """
    <activity
        android:name="org.pocexample.camera.CameraActivity"
        android:exported="false"
        android:screenOrientation="fullSensor" />
    <activity
        android:name="org.pocexample.qrlib.QRScanActivity"
        android:exported="false"
        android:screenOrientation="fullSensor" />

"""

def after_apk_build(toolchain):
    # mutate AndroidManifest.xml
    manifest_fn = "{}/src/main/AndroidManifest.xml".format(
        toolchain._dist.dist_dir)
    with open(manifest_fn, "r") as fd:
        manifest = fd.read()
    
    # check if the ident exists
    if JAVA_IDENT not in manifest:
        # add ident
        manifest = manifest.replace("</application>",
                                    JAVA_IDENT + "</application>")

        # rewrite manifest
        with open(manifest_fn, "w") as fd:
            fd.write(manifest)
