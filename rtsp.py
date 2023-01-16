import argparse
import re
import sys
from functools import singledispatchmethod
from typing import Tuple, TypeVar

import cv2
from loguru import logger

logger.add("file_1.log", rotation="10 MB")
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

parser = argparse.ArgumentParser(description="RTSP stream record.")
parser.add_argument("-l", "--link", required=True, type=str)
parser.add_argument("-o", "--output", type=str, default="output.avi")
parser.add_argument("-d", "--duration", type=float, required=True)

args = parser.parse_args()


ACCESS_MEASURES = {"sec": 1, "min": 60, "hour": 60 * 60, "day": 60 * 60 * 24}
MAX_ACCESS_DIGIT_COUNT = 3

Codec = TypeVar("Codec", bound=int)


class BrokenConnectionException(Exception):
    def __init__(self, msg="Connection was interrupted"):
        super().__init__(msg)


class Capture:
    def __init__(self, source):
        self.source = source


class RTSPCapture(Capture):
    def __init__(self, source: str):
        super().__init__(source)
        self._capture = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        self.current_frame = 0
        self.duration = None

    def update_frame_rate(self):
        fps = self._capture.get(cv2.CAP_PROP_FPS)

        while True:
            if self._capture.isOpened():
                if not self.current_frame % fps:
                    logger.info(f"{self.current_frame // fps} second was recorded")

                if not self.duration:
                    yield self._capture.read()
                elif self.duration * fps > self.current_frame:
                    yield self._capture.read()
                    self.current_frame += 1
                else:
                    break
            else:
                logger.warning("Connection was interrupted, is the link correct ?")
                raise BrokenConnectionException()

    @property
    def width(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


class RTSPVideoWriter:
    def __init__(self, pathname: str, codec: Codec, fps: float, size: Tuple[int, int]) -> None:
        self.output = cv2.VideoWriter(pathname, codec, fps, size)


class RTSPStream:
    def __init__(self, rtsp_link: str) -> None:
        self._rtsp_link = rtsp_link
        self.capture = RTSPCapture(source=self._rtsp_link)
        self._duration = None
        self._is_closed = False

    @singledispatchmethod
    def include_duration(self, duration) -> None:
        raise NotImplementedError("Cannot apply this value to a stream duration")

    @include_duration.register
    def _(self, duration: int | float) -> None:
        """set stream need saved duration as int or float"""
        self._duration = duration

    @include_duration.register
    def _(self, duration: str) -> None:
        """include_duration method get stream need saved duration as string and try parse it"""
        digit_duration = re.findall(r"\d+", duration)
        if not digit_duration or len(digit_duration) >= MAX_ACCESS_DIGIT_COUNT:
            if not digit_duration:
                raise ValueError("Stream duration digit not provided")
            else:
                raise ValueError("Multiple digits not allowed")

        duration_measures = re.findall(r"[a-zA-Z]+", duration)
        if not duration_measures or len(duration_measures) > 1:
            raise ValueError("Check duration measurement correctly filled")
        duration_measure = duration_measures.pop().lower()
        if duration_measure not in ACCESS_MEASURES:
            raise ValueError("Provided measure not accessible")

        validate_duration = float(digit_duration.pop()) * ACCESS_MEASURES.get(duration_measure)
        self._duration = validate_duration

    @property
    def duration(self) -> int | float:
        return self._duration

    def __iter__(self):
        """__iter__ for get capture frame chunk in loop as generator"""
        self.capture.duration = self.duration
        yield from self.capture.update_frame_rate()

    def __str__(self) -> str:
        """User friendly class instance representation"""
        return f"<{self.__class__.__name__}> [{self._rtsp_link}]"


def stream_record(link: str):
    """Recording stream function"""
    rtsp_stream = RTSPStream(link)
    rtsp_stream.include_duration(args.duration)
    codec = cv2.VideoWriter_fourcc("M", "J", "P", "G")

    video_writer = RTSPVideoWriter(args.output, codec, 24, (rtsp_stream.capture.width, rtsp_stream.capture.height))
    logger.info(f"Start recording video stream [{link[:24]}...]")
    for state, frame in rtsp_stream:
        video_writer.output.write(frame)
    else:
        logger.info("Record was successful saved")


def main():
    """Main entry point"""
    stream_record(link=args.link)


# "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4" link example


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.exception("Error recording video stream you stopped stream recording")
    except Exception as e:
        logger.exception(f"Error recording video stream {e}")
