from kivy.lang import Builder
from kivy.utils import platform
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivymd.app import MDApp

from libs import qr_lib

class PocExampleApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Window.clearcolor = self.theme_cls.backgroundColor
        self._activity_bound = False
        self._pending_action = None

        self.__qr_lib = qr_lib.QrWork()
        self.__qr_lib.build()

        return Builder.load_file("main.kv")

    def on_start(self):
        self.append_log("App ready")

    def append_log(self, message):
        box = self.root.ids.log_box
        box.text = f"{box.text}\n{message}"

    def take_photo(self):
        if platform != 'android':
            self.append_log('Photo: only on Android')
        self._f_take_photo(self._ret_scan_load_config)

    def _f_take_photo(self, cb):
        """Respond to the photo scan / choose process"""
        self.append_log("On scan pressed")
        self.__qr_lib.do_photo(cb)

    def scan_qr(self):
        if platform != 'android':
            self.append_log('QR: only on Android')

        self._f_scan_qr(self._ret_scan_load_config)

    def _f_scan_qr(self, cb):
        """Respond to the scan process"""
        self.append_log("On scan pressed")
        self.__qr_lib.do_scan(cb)

    @mainthread
    def _ret_scan_load_config(self, result):
        self.append_log(repr(result))

    @mainthread
    def _result_scan(self, result):
        """"""
        self.__gc.log(result)

if __name__ == '__main__':
    PocExampleApp().run()
