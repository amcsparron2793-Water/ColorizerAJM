import re
from abc import abstractmethod, ABCMeta
from typing import Union, Optional

from ColorizerAJM.errs import InvalidColorInputError
from ColorizerAJM.base_classes import _ColorConverterBasicAttrs


class TqdmMixin(metaclass=ABCMeta):
    ANSI_OCT_ESCAPE_PREFIX = None
    ANSI_HEX_ESCAPE_PREFIX = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.ANSI_OCT_ESCAPE_PREFIX is None or cls.ANSI_HEX_ESCAPE_PREFIX is None:
            raise TypeError("ANSI_OCT_ESCAPE_PREFIX and ANSI_HEX_ESCAPE_PREFIX must be set in the subclass")

    @classmethod
    @abstractmethod
    def ansi_escape_to_hex(cls, ansi_escape: str) -> str:
        ...

    @staticmethod
    def bar_colors() -> dict:
        try:
            from tqdm.std import Bar
            bar_colors = Bar.COLOURS
        except ImportError:
            Bar = None
            bar_colors = dict()
        return bar_colors

    @classmethod
    def to_tqdm_colour(cls, color: Optional[str], allow_none: bool = False) -> Optional[str]:
        """
        Normalize a color value into something suitable for tqdm's colour argument.

        If given an ANSI escape sequence, it returns a hex color.
        If given an existing hex color or normal color name, it returns it unchanged.
        """
        if color is None:
            if allow_none:
                return None
        # if not allow_none, and it is none, then this will catch it
        if not isinstance(color, str):
            raise TypeError(f"color must be a string, not {type(color)}")

        if cls.ANSI_OCT_ESCAPE_PREFIX in color or cls.ANSI_HEX_ESCAPE_PREFIX in color:
            return cls.ansi_escape_to_hex(color)

        elif color.upper() in cls.bar_colors:
            return color.upper()
        else:
            raise InvalidColorInputError(f"Unsupported color: {color!r}")


class ColorConverter(_ColorConverterBasicAttrs):
    @staticmethod
    def rgb_to_hex(red: int, green: int, blue: int) -> str:
        """
        Convert RGB integer values to a hex color string.

        :param red: Red value from 0 to 255.
        :param green: Green value from 0 to 255.
        :param blue: Blue value from 0 to 255.
        :return: Hex color string usable by tqdm, such as "#ff8800".
        """
        for value in (red, green, blue):
            if not 0 <= value <= 255:
                raise ValueError(f"RGB values must be between 0 and 255, not {value}")

        return f"#{red:02x}{green:02x}{blue:02x}"

    @classmethod
    def _check_for_ansi_16(cls, color_index: int):
        if color_index in cls.BASIC_ANSI_RANGE:
            ansi_16_palette = list(cls.ANSI_16_TO_HEX.values())
            return ansi_16_palette[color_index]
        return color_index

    @classmethod
    def _check_for_rgb(cls, color_index: int):
        """
        Conceptually: color_index = red_position * 36 + green_position * 6 + blue_position

        Where each position is between 0 and 5.
        Then each position is mapped to an actual brightness level:
        0 -> 0
        1 -> 95
        2 -> 135
        3 -> 175
        4 -> 215
        5 -> 255

        So the method is converting from:
        ANSI palette position
        to:
        RGB(red, green, blue)

        :param color_index:
        :type color_index:
        :return:
        :rtype:
        """
        if color_index in cls.RGB_RANGE:
            # ANSI color indexes 0–15 are reserved for the basic ANSI colors.
            # So index 16 is actually the first RGB-cube color.
            # To make the math easier, the code shifts the RGB color range down so it starts at 0
            color_index = color_index - 16

            # there are 6 levels of blue in the RGB color cube, thus the modulus by 6
            # blue increments first in the cube, then red, then green, then blue again
            blue = cls.RGB_LEVELS[color_index % 6]

            # Green changes every 6 indexes.
            # Why 6? Because for each green level, blue goes through all 6 possible values.
            # mod 36 keeps the green level within a red block.
            # Each red block contains 6 green levels and 6 blue levels (aka 36 indexes total).
            green = cls.RGB_LEVELS[(color_index % 36) // 6]

            # Each red block contains 6 green levels and 6 blue levels (aka 36 indexes total)
            red = cls.RGB_LEVELS[color_index // 36]

            return cls.rgb_to_hex(red, green, blue)
        return color_index

    @classmethod
    def _calc_grayscale(cls, color_index: int):
        # In RGB, a color is gray when red, green, and blue are all the same value.
        # This calculates the brightness value on the grayscale ramp. The grayscale ramp does not start at pure black 0.
        # It starts at brightness 8, then increases by 10 each step, ie 232 -> 8, 233 -> 18, etc.
        # We multiply by 10 because the brightness increases by approx 10 per step.
        if color_index in cls.GRAYSCALE_RANGE:
            gray = cls.GRAYSCALE_BRIGHTNESS_START + (color_index - 232) * cls.BRIGHTNESS_MULTIPLIER
            return cls.rgb_to_hex(gray, gray, gray)
        return color_index

    @classmethod
    def ansi_256_to_hex(cls, color_index: int) -> str:
        """
        Convert an ANSI 256-color palette index to a hex color string.

        Handles indexes from ANSI escape codes like "\\033[38;5;208m".
        """
        if not 0 <= color_index <= 255:
            raise ValueError(f"ANSI 256 color index must be between 0 and 255, not {color_index}")

        res: Union[int, str] = cls._check_for_ansi_16(color_index)
        if isinstance(res, str):
            return res

        res: Union[int, str] = cls._check_for_rgb(color_index)
        if isinstance(res, str):
            return res

        res: Union[int, str] = cls._calc_grayscale(color_index)
        if isinstance(res, str):
            return res

        raise ValueError(f"Unsupported ANSI 256 color index: {color_index}")

    @classmethod
    def ansi_escape_to_hex(cls, ansi_escape: str) -> str:
        """
        Convert an ANSI foreground/background color escape sequence to a hex color.

        Supported examples:
            "\\033[31m"             -> approximate basic ANSI red
            "\\033[91m"             -> approximate bright red
            "\\033[38;5;208m"       -> ANSI 256-color foreground
            "\\033[48;5;208m"       -> ANSI 256-color background
            "\\033[38;2;255;136;0m" -> truecolor foreground
            "\\033[48;2;255;136;0m" -> truecolor background

        :param ansi_escape: ANSI escape code string.
        :return: Hex color string usable by tqdm.
        """
        numbers = [int(number) for number in re.findall(r"\d+", ansi_escape)]

        if len(numbers) >= 5 and numbers[:2] in ([38, 2], [48, 2]):
            return cls.rgb_to_hex(numbers[2], numbers[3], numbers[4])

        if len(numbers) >= 3 and numbers[:2] in ([38, 5], [48, 5]):
            return cls.ansi_256_to_hex(numbers[2])

        for number in numbers:
            if number in cls.ANSI_16_TO_HEX:
                return cls.ANSI_16_TO_HEX[number]

        raise ValueError(f"Unsupported ANSI color escape sequence: {ansi_escape!r}")
