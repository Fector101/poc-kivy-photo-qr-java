# -*- coding: utf-8 -*-
# libs/qr_lib.py

from functools import partial

from kivy.clock import Clock, mainthread
from kivy.utils import platform

from . import objs
from . import constants as C

def is_android():
    return platform == 'android'

if is_android():
    from jnius import autoclass
    from android import activity as android_activity
    from android.permissions import request_permissions, Permission
    from jnius import cast

class QrWork:
    def __init__(self):
        self._gc = objs.GlobalConfig()

        if is_android():
            self._gc.log("QrWork::android, load java with autoclass")
            self._PythonActivity = autoclass("org.kivy.android.PythonActivity")
            self._Intent = autoclass("android.content.Intent")
            self._Activity = autoclass("android.app.Activity")
            self._ActivityQR = autoclass("org.pocexample.qrlib.QRScanActivity")
            self._ActivityCamera = autoclass("org.pocexample.camera.CameraActivity")
        else:
            self._gc.log("QrWork::no android, skipping")
        self._cb_end_scan = None
        
    def build(self):
        """"""
        if is_android():
            self._gc.log("QrWork::start activity")
            android_activity.bind(on_activity_result=self._on_activity_result)
    
    def do_scan(self, cb_end_scan):
        """"""
        self._cb_end_scan = cb_end_scan
        if is_android():
            request_permissions(
                [Permission.CAMERA, Permission.VIBRATE],
                self._call_lib_scan
            )
        else:
            #handle pc
            Clock.schedule_once(partial(self._on_activity_result, C.C_SCAN_QR, None, None), 0)


    def do_photo(self, cb_end_scan):
        """"""
        self._cb_end_scan = cb_end_scan
        if is_android():
            request_permissions(
                [Permission.CAMERA, Permission.VIBRATE],
                self._call_lib_photo
            )
        else:
            #handle pc
            Clock.schedule_once(partial(self._on_activity_result, C.C_SCAN_CAMERA, None, None), 0)
        
    def _call_lib_scan(self, permissions, grants):
        """"""
        if is_android():
            if not all(grants):
                self._gc.log("QrWork::Not all permits: %s" % repr(grants))
                return
            activity = cast("android.app.Activity", self._PythonActivity.mActivity)
            intent = self._Intent(activity, self._ActivityQR)
            activity.startActivityForResult(intent, C.C_SCAN_QR)
        else:
            #handle pc
            Clock.schedule_once(partial(self._on_activity_result, C.C_SCAN_QR, None, None), 0)

    
    def _call_lib_photo(self, permissions, grants):
        """"""
        if is_android():
            if not all(grants):
                self._gc.log("QrWork::Not all permits: %s" % repr(grants))
                return
            activity = cast("android.app.Activity", self._PythonActivity.mActivity)
            intent = self._Intent(activity, self._ActivityCamera)
            activity.startActivityForResult(intent, C.C_SCAN_CAMERA)
        else:
            #handle pc
            pass


    @mainthread
    def _on_activity_result(self, request_code, result_code, intent, *args):
        """Call from java/android if on android, otherwiise diretly from Clock.schedule_interval
            *args is used only because schedule_interval pass dt. @https://kivy.org/doc/stable/api-kivy.clock.html
        """
        self._gc.log("QrWork::_on_activity_result: %s, %s" % (request_code, repr(result_code)))
        if request_code not in (C.C_SCAN_QR,  C.C_SCAN_CAMERA):
            return
        
        if is_android():
            if result_code == self._Activity.RESULT_OK and intent:
                if request_code == C.C_SCAN_QR:
                    get_str_data = self._ActivityQR.EXTRA_QR_DATA
                else:
                    get_str_data = self._ActivityCamera.EXTRA_PHOTO_PATH
                value = intent.getStringExtra(get_str_data)
                result = (C.C_SCAN_OK, value)
            else:
                msg = "QrWork::Timeout / Users ends"
                result = (C.C_SCAN_KO, msg)
        else:
            #handle pc
            result = "Not android"

        if callable(self._cb_end_scan):
            Clock.schedule_once( lambda dt: self._cb_end_scan(result), 0 )
        else:
            self._gc.log(f"Error: {self._cb_end_scan} not collable. Skip")
