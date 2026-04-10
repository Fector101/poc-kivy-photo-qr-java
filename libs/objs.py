import sys
import logging
import logging.handlers

from . import constants as C

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logging(metaclass=Singleton):
    def __init__(self, debug: int = False):
        self._debug = debug
        self._log = logging.getLogger("MySw")
        self._log.setLevel(logging.DEBUG)

        if self._log.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # console
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        self._log.addHandler(stream_handler)

    def log(self, *args):
        self._write(*args)

    def error(self, *args):
        self._write(*args, error=1)

    def exception(self, *args):
        self._write(*args, exception=1)

    def debug(self, *args):
        self._write(*args, debug=1)

    def get_log_file(self):
        return getattr(self, "log_file", None)

    def _write(self, *args, **kw):
        if not self._debug:
            return

        if len(args) == 1:
            v = args[0]
        else:
            v = ";".join([str(x) for x in args])

        if "debug" in kw:
            f_log = self._log.debug
        elif "exception" in kw:
            f_log = self._log.exception
        elif "error" in kw:
            f_log = self._log.error
        else:
            f_log = self._log.info

        f_log(str(v).replace("\n", ";"))

    def __call__(self, *args):
        self.log(*args)



class GlobalConfig(metaclass=Singleton):
    """Global container. Here we have:
        - configurations objects
        - useful functions used overall
    """
    def __init__(self):
        """"""
        self.log = Logging(C.C_DEBUG)
