import ctypes
import os
import time


class GreenBibleNDI:
    def __init__(self, source_name="GREENBIBLE"):
        self.source_name = source_name
        self.dll = None
        self.initialized = False

        dll_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Processing.NDI.Lib.x64.dll"
        )

        self.dll = ctypes.CDLL(dll_path)

        # NDI 6.x initialization
        self.dll.NDIlib_initialize.restype = ctypes.c_bool
        self.dll.NDIlib_initialize.argtypes = []

        self.dll.NDIlib_destroy.argtypes = []
        self.dll.NDIlib_destroy.restype = None

        if not self.dll.NDIlib_initialize():
            raise RuntimeError("NDI initialization failed")

        self.initialized = True
        print("GREENBIBLE NDI: INITIALIZED")
        print(f"GREENBIBLE NDI SOURCE: {self.source_name}")

    def close(self):
        if self.initialized and self.dll:
            self.dll.NDIlib_destroy()
            self.initialized = False
            print("GREENBIBLE NDI: CLOSED")

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass