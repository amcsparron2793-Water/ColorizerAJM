"""
ColorizerAJM.py

adapted from https://medium.com/@ryan_forrester_/adding-color-to-python-terminal-output-a-complete-guide-147fcb1c335f

uses ANSI escape codes to colorize terminal output

"""
import random
from typing import Union

from _version import __version__


class InvalidColorCode(Exception):
    ...


class Colorizer:
    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'
    YELLOW = 'YELLOW'
    MAGENTA = 'MAGENTA'
    CYAN = 'CYAN'
    WHITE = 'WHITE'

    DEFAULT_COLOR_CODES = {
        RED: '\033[91m',
        GREEN: '\033[92m',
        BLUE: '\033[94m',
        YELLOW: '\033[93m',
        MAGENTA: '\033[95m',
        CYAN: '\033[96m',
        WHITE: '\033[97m',
    }

    RESET_COLOR_CODE = '\033[0m'
    CUSTOM_COLOR_PREFIX = '\033[38;5;'
    ALL_VALID_CODES_RANGE = range(0, 256)

    def __init__(self, custom_colors: dict = None, **kwargs):
        """
        Uses ANSI escape codes to colorize terminal output

        :param custom_colors: A dictionary containing custom colors for the software.
        :type custom_colors: dict
        """
        self.ignore_invalid_colors = kwargs.get('ignore_invalid_colors', False)

        self._custom_colors = custom_colors or {}

    @property
    def custom_colors(self):
        temp_dict = {}
        for x in self._custom_colors.items():
            if isinstance(x[1], int):
                x = {x[0].upper(): self.get_color_code({x[0]: x[1]})}
            elif isinstance(x[1], str) and x[1].startswith('\033'):
                x = {x[0].upper(): x[1]}
            temp_dict.update(x)
        self._custom_colors = temp_dict

        return self._custom_colors

    @property
    def all_available_colors(self):
        return list(Colorizer.DEFAULT_COLOR_CODES.keys()) + list(self.custom_colors.keys())

    @staticmethod
    def random_color():
        return (f'{Colorizer.CUSTOM_COLOR_PREFIX}'
                f'{random.randint(Colorizer.ALL_VALID_CODES_RANGE[0],
                                  Colorizer.ALL_VALID_CODES_RANGE[-1])}m')

    def colorize(self, text, color=None, bold=False):
        """Add color to text, first looking in the class dict DEFAULT_COLOR_CODES, then looking in the custom_colors dict,
         and handle reset automatically"""
        if not color:
            color_code = self.random_color()
        else:
            color_code = self.get_color_code(color)

        if bold:
            color_code = self.make_bold(color_code)
        return f"{color_code}{text}{Colorizer.RESET_COLOR_CODE}"

    def print_color(self, text, **kwargs):
        color = kwargs.get('color', None)
        bold = kwargs.get('bold', False)
        print(self.colorize(text, color, bold))

    @staticmethod
    def stringify_color_id(color_id: int):
        """builds the full custom color ANSI escape code from the color_id"""
        if color_id in Colorizer.ALL_VALID_CODES_RANGE:
            return f'{Colorizer.CUSTOM_COLOR_PREFIX}{color_id}m'
        else:
            raise InvalidColorCode("color_id must be an integer between 0 and 255")

    def get_color_code(self, color: Union[str, dict]) -> str:
        """Retrieve color code from default or custom colors."""
        if isinstance(color, dict):
            color, color_id = [x for x in color.items()][0] if color else [None, None]
            return self.stringify_color_id(color_id)
        elif isinstance(color, int):
            color_id = color
            return self.get_color_code(self.stringify_color_id(color_id))

        elif isinstance(color, str):
            full_str = Colorizer.DEFAULT_COLOR_CODES.get(color.upper(),
                                                         self.custom_colors.get(color.upper(), ''))
            if full_str != '':
                return full_str
            else:
                if not self.ignore_invalid_colors:
                    raise InvalidColorCode('given color did not match any of the available colors')
                return full_str
        else:
            raise AttributeError("color attribute must be a string or a dictionary")

    @staticmethod
    def make_bold(color_code):
        return color_code.replace('[', '[1;')

    def pretty_print_all_available_colors(self):
        print('All Available Colors: ')
        for color in self.all_available_colors:
            print(self.colorize(color, color))

    def example_usage(self):
        # Usage examples
        self.print_color("Warning: Low disk space", color="yellow")
        self.print_color("Error: Connection failed", color="red")
        self.print_color("Success: Test passed", color="green")
        self.pretty_print_all_available_colors()


if __name__ == "__main__":
    test_custom_colors = {
        'light_blue': Colorizer.CUSTOM_COLOR_PREFIX + '25m',
        'light_pink': 210
    }
    c = Colorizer(custom_colors=test_custom_colors, ignore_invalid_colors=False)
    c.example_usage()
