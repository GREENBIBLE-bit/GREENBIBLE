import ctypes
import os
import threading
import time

from PIL import Image, ImageDraw, ImageFont


BASE = os.path.dirname(os.path.abspath(__file__))
DLL = os.path.join(BASE, "Processing.NDI.Lib.x64.dll")

WIDTH = 1280
HEIGHT = 720
FPS = 30

# Scripture presentation style
DEFAULT_SCRIPTURE_BG = "#000000"
DEFAULT_SCRIPTURE_TEXT = "#FFFFFF"
DEFAULT_SCRIPTURE_FONT_SIZE = 38
DEFAULT_SCRIPTURE_BOLD = False
DEFAULT_SCRIPTURE_ALIGN = "center"
DEFAULT_REFERENCE_COLOR = "#FFFFFF"
DEFAULT_REFERENCE_FONT_SIZE = 34
DEFAULT_REFERENCE_BOLD = True
DEFAULT_REFERENCE_POSITION = "top left"


class SendCreate(ctypes.Structure):
    _fields_ = [
        ("p_ndi_name", ctypes.c_char_p),
        ("p_groups", ctypes.c_char_p),
        ("clock_video", ctypes.c_bool),
        ("clock_audio", ctypes.c_bool),
    ]


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


class GreenBibleNDI:
    def __init__(self):
        self.ndi = ctypes.CDLL(DLL)

        self.ndi.NDIlib_initialize.restype = ctypes.c_bool

        if not self.ndi.NDIlib_initialize():
            raise RuntimeError("NDI initialization failed")

        self.ndi.NDIlib_send_create.argtypes = [
            ctypes.POINTER(SendCreate),
            ctypes.c_void_p
        ]
        self.ndi.NDIlib_send_create.restype = ctypes.c_void_p

        self.ndi.NDIlib_send_send_video_v2.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(VideoFrame)
        ]
        self.ndi.NDIlib_send_send_video_v2.restype = None

        self.ndi.NDIlib_send_destroy.argtypes = [
            ctypes.c_void_p
        ]
        self.ndi.NDIlib_send_destroy.restype = None

        settings = SendCreate(
            b"GREENBIBLE",
            None,
            True,
            False
        )

        self.sender = self.ndi.NDIlib_send_create(
            ctypes.byref(settings),
            None
        )

        if not self.sender:
            self.ndi.NDIlib_destroy()
            raise RuntimeError("Could not create GREENBIBLE NDI sender")

        self.running = True
        self.lock = threading.Lock()

        self.reference = "GREENBIBLE"
        self.text = "Waiting for Scripture..."

        # Scripture presentation style
        self.scripture_bg = DEFAULT_SCRIPTURE_BG
        self.scripture_text = DEFAULT_SCRIPTURE_TEXT
        self.scripture_font_size = DEFAULT_SCRIPTURE_FONT_SIZE
        self.scripture_bold = DEFAULT_SCRIPTURE_BOLD
        self.scripture_align = DEFAULT_SCRIPTURE_ALIGN

        # Scripture reference presentation style
        self.reference_color = DEFAULT_REFERENCE_COLOR
        self.reference_font_size = DEFAULT_REFERENCE_FONT_SIZE
        self.reference_bold = DEFAULT_REFERENCE_BOLD
        self.reference_position = DEFAULT_REFERENCE_POSITION

        self.buffer = None
        self.frame = None

        self._render()

        self.thread = threading.Thread(
            target=self._send_loop,
            daemon=True
        )

        self.thread.start()

        print("GREENBIBLE NDI: ACTIVE")
        print("GREENBIBLE NDI SOURCE: GREENBIBLE")

    def _font(self, filename, size):
        path = os.path.join(
            os.environ.get("WINDIR", r"C:\Windows"),
            "Fonts",
            filename
        )

        return ImageFont.truetype(path, size)

    def _render(self):
        # Use the selected Scripture background color
        image = Image.new(
            "RGB",
            (WIDTH, HEIGHT),
            getattr(self, "scripture_bg", DEFAULT_SCRIPTURE_BG)
        )

        draw = ImageDraw.Draw(image)

        reference_font = self._font(
            "arialbd.ttf" if getattr(
                self,
                "reference_bold",
                DEFAULT_REFERENCE_BOLD
            ) else "arial.ttf",
            getattr(
                self,
                "reference_font_size",
                DEFAULT_REFERENCE_FONT_SIZE
            )
        )

        verse_font = self._font(
            "arialbd.ttf" if getattr(
                self, "scripture_bold", False
            ) else "arial.ttf",
            getattr(
                self,
                "scripture_font_size",
                DEFAULT_SCRIPTURE_FONT_SIZE
            )
        )


                # HEADER
               # HEADER
        # Bible = reference + KJV
        # Song / Announcement = no KJV

        if self.reference:
            reference_box = draw.textbbox(
                (0, 0),
                self.reference,
                font=reference_font
            )

            reference_width = (
                reference_box[2] - reference_box[0]
            )

            reference_position = getattr(
                self,
                "reference_position",
                DEFAULT_REFERENCE_POSITION
            )

            # Bible references show KJV beside the reference.
            is_bible = self.reference not in (
                "SONG",
                "ANNOUNCEMENT"
            )

            if is_bible:
                kjv_box = draw.textbbox(
                    (0, 0),
                    "KJV",
                    font=reference_font
                )

                kjv_width = (
                    kjv_box[2] - kjv_box[0]
                )

                kjv_gap = 25

                if reference_position == "top center":
                    total_width = (
                        reference_width
                        + kjv_gap
                        + kjv_width
                    )

                    reference_x = (
                        WIDTH - total_width
                    ) / 2

                elif reference_position == "top right":
                    total_width = (
                        reference_width
                        + kjv_gap
                        + kjv_width
                    )

                    reference_x = (
                        WIDTH
                        - total_width
                        - 60
                    )

                else:
                    reference_x = 60

                draw.text(
                    (
                        reference_x,
                        45
                    ),
                    self.reference,
                    font=reference_font,
                    fill=getattr(
                        self,
                        "reference_color",
                        DEFAULT_REFERENCE_COLOR
                    )
                )

                draw.text(
                    (
                        reference_x
                        + reference_width
                        + kjv_gap,
                        45
                    ),
                    "KJV",
                    font=reference_font,
                    fill="yellow"
                )

            else:
                # Songs and announcements show their header
                # without KJV.
                if reference_position == "top center":
                    reference_x = (
                        WIDTH - reference_width
                    ) / 2

                elif reference_position == "top right":
                    reference_x = (
                        WIDTH - reference_width - 60
                    )

                else:
                    reference_x = 60

                draw.text(
                    (
                        reference_x,
                        45
                    ),
                    self.reference,
                    font=reference_font,
                    fill=getattr(
                        self,
                        "reference_color",
                        DEFAULT_REFERENCE_COLOR
                    )
                )

        # Verse wrapping
        words = self.text.split()
        lines = []
        current = ""

        max_width = 1100

        for word in words:

            test = (
                word
                if not current
                else current + " " + word
            )

            box = draw.textbbox(
                (0, 0),
                test,
                font=verse_font
            )

            if box[2] - box[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)

                current = word

        if current:
            lines.append(current)

        line_height = max(
            50,
            int(
                getattr(
                    self,
                    "scripture_font_size",
                    DEFAULT_SCRIPTURE_FONT_SIZE
                ) * 1.35
            )
        )
        total_height = len(lines) * line_height

        start_y = (
            (HEIGHT - total_height) / 2
        )

        for line in lines:

            box = draw.textbbox(
                (0, 0),
                line,
                font=verse_font
            )

            line_width = (
                box[2] - box[0]
            )

            alignment = getattr(
                self,
                "scripture_align",
                DEFAULT_SCRIPTURE_ALIGN
            )

            if alignment == "left":
                x = 80
            elif alignment == "right":
                x = WIDTH - line_width - 80
            else:
                x = (
                    WIDTH - line_width
                ) / 2

            draw.text(
                (x, start_y),
                line,
                font=verse_font,
                fill=getattr(
                    self,
                    "scripture_text",
                    DEFAULT_SCRIPTURE_TEXT
                )
            )

            start_y += line_height

        # Convert RGB -> BGRA
        raw = image.convert("RGBA").tobytes("raw", "BGRA")

        self.buffer = (
            ctypes.c_ubyte * len(raw)
        ).from_buffer_copy(raw)

        BGRA = (
            ord("B")
            | (ord("G") << 8)
            | (ord("R") << 16)
            | (ord("A") << 24)
        )

        self.frame = VideoFrame(
            WIDTH,
            HEIGHT,
            BGRA,
            FPS,
            1,
            WIDTH / HEIGHT,
            1,
            int(time.time() * 10000000),
            self.buffer,
            WIDTH * 4,
            None,
            0
        )

    def set_scripture_style(
        self,
        background=None,
        text_color=None,
        font_size=None,
        bold=None,
        alignment=None,
        reference_color=None,
        reference_font_size=None,
        reference_bold=None,
        reference_position=None
    ):
        with self.lock:
            if background is not None:
                self.scripture_bg = background

            if text_color is not None:
                self.scripture_text = text_color

            if font_size is not None:
                self.scripture_font_size = int(font_size)

            if bold is not None:
                self.scripture_bold = bool(bold)

            if alignment is not None:
                self.scripture_align = alignment

            if reference_color is not None:
                self.reference_color = reference_color

            if reference_font_size is not None:
                self.reference_font_size = int(
                    reference_font_size
                )

            if reference_bold is not None:
                self.reference_bold = bool(
                    reference_bold
                )

            if reference_position is not None:
                self.reference_position = reference_position

            self._render()

    def update(self, reference, text):

        with self.lock:

            self.reference = reference
            self.text = text

            self.media_image_path = None

            self._render()



    def stop_video(self):
        try:
            self.video_running = False
            if hasattr(self, "video_thread") and self.video_thread:
                self.video_thread.join(timeout=1.0)
        except Exception:
            pass
        self.video_thread = None

    def seek_video(self, seconds):
        try:
            import cv2

            if not getattr(self, "video_path", None):
                return

            # Stop the current video thread
            was_running = getattr(self, "video_running", False)
            self.video_running = False

            if hasattr(self, "video_thread") and self.video_thread:
                self.video_thread.join(timeout=1.0)

            cap = cv2.VideoCapture(self.video_path)

            if not cap.isOpened():
                print("MEDIA VIDEO NDI: SEEK FAILED")
                return

            fps = cap.get(cv2.CAP_PROP_FPS)

            if not fps or fps <= 1 or fps > 120:
                fps = 30.0

            current = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            duration = (
                cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
            )

            target = max(
                0,
                min(current + seconds, duration)
            )

            cap.set(
                cv2.CAP_PROP_POS_MSEC,
                target * 1000
            )

            ok, frame = cap.read()

            if ok:
                from PIL import Image, ImageOps

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                image = Image.fromarray(rgb).convert("RGB")

                fitted = ImageOps.contain(
                    image,
                    (WIDTH, HEIGHT)
                )

                canvas = Image.new(
                    "RGB",
                    (WIDTH, HEIGHT),
                    "black"
                )

                x = (WIDTH - fitted.width) // 2
                y = (HEIGHT - fitted.height) // 2

                canvas.paste(
                    fitted,
                    (x, y)
                )

                raw = canvas.convert(
                    "RGBA"
                ).tobytes(
                    "raw",
                    "BGRA"
                )

                buffer = (
                    ctypes.c_ubyte * len(raw)
                ).from_buffer_copy(raw)

                BGRA = (
                    ord("B")
                    | (ord("G") << 8)
                    | (ord("R") << 16)
                    | (ord("A") << 24)
                )

                with self.lock:
                    self.buffer = buffer
                    self.frame = VideoFrame(
                        WIDTH,
                        HEIGHT,
                        BGRA,
                        FPS,
                        1,
                        WIDTH / HEIGHT,
                        1,
                        int(time.time() * 10000000),
                        self.buffer,
                        WIDTH * 4,
                        None,
                        0
                    )

                print(
                    "MEDIA VIDEO NDI: SEEK ->",
                    round(target, 2),
                    "seconds"
                )

            cap.release()

            self.video_running = was_running

            if was_running:
                self.video_thread = threading.Thread(
                    target=self._video_loop_restart,
                    daemon=True
                )
                self.video_thread.start()

        except Exception as e:
            print("MEDIA VIDEO NDI SEEK ERROR:", e)

    def _video_loop_restart(self):
        self.update_video(self.video_path)

    def pause_video(self):
        self.video_paused = True
        print("MEDIA VIDEO NDI: PAUSED")

    def resume_video(self):
        self.video_paused = False
        print("MEDIA VIDEO NDI: RESUMED")

    def update_video(self, video_path):
        import cv2
        import threading
        import time
        from PIL import Image, ImageOps

        self.stop_video()

        self.video_running = True
        self.video_paused = False
        self.video_path = video_path

        def video_loop():
            try:
                cap = cv2.VideoCapture(video_path)

                if not cap.isOpened():
                    print("MEDIA VIDEO NDI ERROR: Could not open video")
                    self.video_running = False
                    return

                fps = cap.get(cv2.CAP_PROP_FPS)

                if not fps or fps <= 1 or fps > 120:
                    fps = 30.0

                frame_delay = 1.0 / fps

                print("MEDIA VIDEO NDI: MOVING VIDEO ACTIVE")
                print("MEDIA VIDEO NDI FPS:", fps)

                while self.video_running:

                    if self.video_paused:
                        time.sleep(0.05)
                        continue

                    start_time = time.time()

                    ok, frame = cap.read()

                    if not ok:
                        break

                    rgb = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB
                    )

                    image = Image.fromarray(rgb).convert("RGB")

                    fitted = ImageOps.contain(
                        image,
                        (WIDTH, HEIGHT)
                    )

                    canvas = Image.new(
                        "RGB",
                        (WIDTH, HEIGHT),
                        "black"
                    )

                    x = (WIDTH - fitted.width) // 2
                    y = (HEIGHT - fitted.height) // 2

                    canvas.paste(
                        fitted,
                        (x, y)
                    )

                    raw = canvas.convert(
                        "RGBA"
                    ).tobytes(
                        "raw",
                        "BGRA"
                    )

                    buffer = (
                        ctypes.c_ubyte * len(raw)
                    ).from_buffer_copy(raw)

                    BGRA = (
                        ord("B")
                        | (ord("G") << 8)
                        | (ord("R") << 16)
                        | (ord("A") << 24)
                    )

                    new_frame = VideoFrame(
                        WIDTH,
                        HEIGHT,
                        BGRA,
                        FPS,
                        1,
                        WIDTH / HEIGHT,
                        1,
                        int(time.time() * 10000000),
                        buffer,
                        WIDTH * 4,
                        None,
                        0
                    )

                    with self.lock:
                        self.buffer = buffer
                        self.frame = new_frame
                        self.reference = ""
                        self.text = ""

                    elapsed = time.time() - start_time
                    delay = max(0.001, frame_delay - elapsed)

                    time.sleep(delay)

                cap.release()

                print("MEDIA VIDEO NDI: STOPPED")

            except Exception as e:
                print("MEDIA VIDEO NDI ERROR:", e)
                self.video_running = False

        self.video_thread = threading.Thread(
            target=video_loop,
            daemon=True
        )

        self.video_thread.start()

    def update_image(self, image_path):

        self.stop_video()

        from PIL import Image, ImageOps

        with self.lock:

            image = Image.open(image_path).convert("RGB")

            # Fit image into the 1280x720 NDI canvas
            fitted = ImageOps.contain(
                image,
                (WIDTH, HEIGHT)
            )

            canvas = Image.new(
                "RGB",
                (WIDTH, HEIGHT),
                "black"
            )

            x = (WIDTH - fitted.width) // 2
            y = (HEIGHT - fitted.height) // 2

            canvas.paste(
                fitted,
                (x, y)
            )

            raw = canvas.convert("RGBA").tobytes(
                "raw",
                "BGRA"
            )

            self.buffer = (
                ctypes.c_ubyte * len(raw)
            ).from_buffer_copy(raw)

            BGRA = (
                ord("B")
                | (ord("G") << 8)
                | (ord("R") << 16)
                | (ord("A") << 24)
            )

            self.reference = ""
            self.text = ""

            self.frame = VideoFrame(
                WIDTH,
                HEIGHT,
                BGRA,
                FPS,
                1,
                WIDTH / HEIGHT,
                1,
                int(time.time() * 10000000),
                self.buffer,
                WIDTH * 4,
                None,
                0
            )

    def _send_loop(self):

        while self.running:

            with self.lock:

                if self.frame is not None:

                    self.frame.timecode = int(
                        time.time() * 10000000
                    )

                    self.ndi.NDIlib_send_send_video_v2(
                        self.sender,
                        ctypes.byref(self.frame)
                    )

            time.sleep(1 / FPS)

    def close(self):

        if not self.running:
            return

        self.running = False

        if self.thread.is_alive():
            self.thread.join(timeout=2)

        if self.sender:
            self.ndi.NDIlib_send_destroy(
                self.sender
            )

            self.sender = None

        self.ndi.NDIlib_destroy()

        print("GREENBIBLE NDI: CLOSED")


ndi_output = None


def start():
    global ndi_output

    if ndi_output is None:
        ndi_output = GreenBibleNDI()

    return ndi_output


def update(reference, text):
    if ndi_output is not None:
        ndi_output.update(
            reference,
            text
        )


def close():
    global ndi_output

    if ndi_output is not None:
        ndi_output.close()
        ndi_output = None