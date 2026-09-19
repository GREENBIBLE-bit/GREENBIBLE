import ctypes
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DLL = os.path.join(BASE, "Processing.NDI.Lib.x64.dll")

ndi = ctypes.CDLL(DLL)

# -----------------------------
# NDI INITIALIZATION
# -----------------------------

ndi.NDIlib_initialize.restype = ctypes.c_bool

if not ndi.NDIlib_initialize():
    raise RuntimeError("NDI initialization failed")

print("NDI initialized")


# -----------------------------
# NDI SEND SETTINGS
# -----------------------------

class SendCreate(ctypes.Structure):
    _fields_ = [
        ("p_ndi_name", ctypes.c_char_p),
        ("p_groups", ctypes.c_char_p),
        ("clock_video", ctypes.c_bool),
        ("clock_audio", ctypes.c_bool),
    ]


ndi.NDIlib_send_create.argtypes = [
    ctypes.POINTER(SendCreate),
    ctypes.c_void_p
]

ndi.NDIlib_send_create.restype = ctypes.c_void_p


settings = SendCreate(
    b"GREENBIBLE",
    None,
    True,
    False
)

sender = ndi.NDIlib_send_create(
    ctypes.byref(settings),
    None
)

if not sender:
    ndi.NDIlib_destroy()
    raise RuntimeError("Could not create NDI sender")

print("GREENBIBLE NDI SENDER CREATED")


# -----------------------------
# NDI VIDEO FRAME
# -----------------------------

class VideoFrame(ctypes.Structure):
    _fields_ = [
        ("xres", ctypes.c_int),
        ("yres", ctypes.c_int),
        ("FourCC", ctypes.c_int),
        ("frame_rate_N", ctypes.c_int),
        ("frame_rate_D", ctypes.c_int),
        ("picture_aspect_ratio", ctypes.c_float),
        ("frame_format_type", ctypes.c_int),
        ("timecode", ctypes.c_int64),
        ("p_data", ctypes.POINTER(ctypes.c_ubyte)),
        ("line_stride_in_bytes", ctypes.c_int),
        ("p_metadata", ctypes.c_char_p),
        ("timestamp", ctypes.c_int64),
    ]


ndi.NDIlib_send_send_video_v2.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(VideoFrame)
]

ndi.NDIlib_send_send_video_v2.restype = None


# -----------------------------
# VIDEO SIZE
# -----------------------------

WIDTH = 1280
HEIGHT = 720

buffer_size = WIDTH * HEIGHT * 4

buffer = (ctypes.c_ubyte * buffer_size)()


# -----------------------------
# CREATE TEST IMAGE
# -----------------------------

for y in range(HEIGHT):
    for x in range(WIDTH):

        i = (y * WIDTH + x) * 4

        # White center rectangle
        if 250 < x < 1030 and 250 < y < 470:

            buffer[i] = 255
            buffer[i + 1] = 255
            buffer[i + 2] = 255
            buffer[i + 3] = 255

        # Dark background
        else:

            buffer[i] = 30
            buffer[i + 1] = 30
            buffer[i + 2] = 30
            buffer[i + 3] = 255


# -----------------------------
# BGRA FOURCC
# -----------------------------

BGRA = (
    ord("B")
    | (ord("G") << 8)
    | (ord("R") << 16)
    | (ord("A") << 24)
)


# -----------------------------
# CREATE FRAME
# -----------------------------

frame = VideoFrame(
    WIDTH,
    HEIGHT,
    BGRA,
    30,
    1,
    WIDTH / HEIGHT,
    1,
    0,
    buffer,
    WIDTH * 4,
    None,
    0
)


# -----------------------------
# START CONTINUOUS STREAM
# -----------------------------

print()
print("======================================")
print(" GREENBIBLE NDI VIDEO IS LIVE")
print("======================================")
print("Source: GREENBIBLE")
print("Resolution: 1280 x 720")
print("Frame rate: 30 FPS")
print()
print("Open NDI Studio Monitor or vMix.")
print("Look for: GREENBIBLE")
print()
print("Press CTRL+C to stop.")
print("======================================")
print()


try:

    while True:

        ndi.NDIlib_send_send_video_v2(
            sender,
            ctypes.byref(frame)
        )

        time.sleep(1 / 30)


except KeyboardInterrupt:

    print()
    print("Stopping GREENBIBLE NDI...")


finally:

    # Correct 64-bit sender handle
    ndi.NDIlib_send_destroy.argtypes = [
        ctypes.c_void_p
    ]

    ndi.NDIlib_send_destroy.restype = None

    ndi.NDIlib_send_destroy(sender)

    ndi.NDIlib_destroy()

    print("GREENBIBLE NDI CLOSED")