from . import errs
from abc import abstractmethod
from typing import Union, Tuple


class _ColorizerBasicAttrs:
    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'
    YELLOW = 'YELLOW'
    MAGENTA = 'MAGENTA'
    CYAN = 'CYAN'
    WHITE = 'WHITE'
    GRAY = 'GRAY'
    LIGHT_GRAY = 'LIGHT_GRAY'
    BLACK = 'BLACK'

    DEFAULT_COLOR_CODES = {
        RED: '\033[91m',
        GREEN: '\033[92m',
        BLUE: '\033[94m',
        YELLOW: '\033[93m',
        MAGENTA: '\033[95m',
        CYAN: '\033[96m',
        WHITE: '\033[97m',
        GRAY: '\x1b[90m',
        LIGHT_GRAY: '\x1b[37m',
        BLACK: '\x1b[30m'
    }

    RESET_COLOR_CODE = '\033[0m'
    CUSTOM_COLOR_PREFIX = '\033[38;5;'
    RGBA_COLOR_PREFIX = '\033[38;2;'
    COLOR_SUFFIX = 'm'
    ALL_VALID_CODES_RANGE = range(0, 256)


class _BaseColorizer(_ColorizerBasicAttrs):
    def __init__(self, **kwargs):
        self.ignore_invalid_colors = kwargs.get('ignore_invalid_colors', False)

    @property
    @abstractmethod
    def custom_colors(self):
        ...

    @staticmethod
    def stringify_color_id(color_id: Union[int, tuple]):
        """ Converts a color ID (integer or RGB tuple) into a string format for colorization.
            - For an integer within the valid range (0-255), returns the ANSI escape code for the color.
            - For a tuple of 3 integers (each in the range 0-255), returns the RGB ANSI escape code.
            Raises:
                InvalidColorCodeError: If the input is not a valid color ID. """
        if isinstance(color_id, int):
            if color_id in _BaseColorizer.ALL_VALID_CODES_RANGE:
                return f'{_BaseColorizer.CUSTOM_COLOR_PREFIX}{color_id}{_BaseColorizer.COLOR_SUFFIX}'
            else:
                raise errs.InvalidColorCodeError("color_id must be an integer between 0 and 255")
        elif isinstance(color_id, tuple):
            if len(color_id) == 3 and all(c in _BaseColorizer.ALL_VALID_CODES_RANGE for c in color_id):
                return f'{_BaseColorizer.RGBA_COLOR_PREFIX}{color_id[0]};{color_id[1]};{color_id[2]}{_BaseColorizer.COLOR_SUFFIX}'
            raise errs.InvalidColorCodeError()

    def _parse_color_string(self, color_string: str):
        """
        Parses a color string and returns the corresponding color code.
        If the color string is not found in the default color codes dictionary or the custom colors dictionary,
        it returns an empty string.
        If the 'ignore_invalid_colors' flag is not set, it raises an InvalidColorCodeError exception.
        """
        full_str = _BaseColorizer.DEFAULT_COLOR_CODES.get(color_string.upper(),
                                                          self.custom_colors.get(color_string.upper(), ''))
        if full_str != '':
            return full_str
        else:
            if not self.ignore_invalid_colors:
                raise errs.InvalidColorCodeError('given color did not match any of the available colors')
            return full_str

    def get_color_code(self, color: Union[str, dict, int, Tuple[int, int, int]]) -> str:
        """
        A method to retrieve color code based on the input provided.
        The input can be a string, dictionary, or integer representing the color.
        If a dictionary is provided, it extracts the color and color ID and returns the color code.
        If an integer is provided, it converts it to color code using the color ID.
        For a string, it parses the color string and returns the corresponding color code.
        If the input is not of type str, dict, or int, it raises an AttributeError.
        """
        if isinstance(color, dict):
            color, color_id = [x for x in color.items()][0] if color else [None, None]
            return self.stringify_color_id(color_id)
        elif isinstance(color, int):
            color_id = color
            return self.get_color_code(self.stringify_color_id(color_id))
        elif isinstance(color, tuple):
            return self.stringify_color_id(color)
        elif isinstance(color, str):
            return self._parse_color_string(color)
        else:
            raise AttributeError(f"color attribute must be a string or a dictionary, not {type(color).__name__}")