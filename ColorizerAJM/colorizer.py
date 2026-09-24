"""
colorizer.py

adapted from https://medium.com/@ryan_forrester_/adding-color-to-python-terminal-output-a-complete-guide-147fcb1c335f

uses ANSI escape codes to colorize terminal output

"""
import random
import re
from typing import Union, Tuple

from ColorizerAJM import CustomColorColorizer
from ColorizerAJM.errs import MissingColorDefinitionError, InvalidColorInputError


# TODO: add in background color functionality
# TODO: work on CustomColorColorizer/_init decupilization
class Colorizer(CustomColorColorizer):
    """ Class for coloring text in the terminal with ANSI escape codes. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.custom_color_file_path.is_file():
            self.read_custom_colors()

    @property
    def all_loaded_colors(self):
        """
        @return a list of all loaded colors including default color codes and custom colors
        """
        return list(Colorizer.DEFAULT_COLOR_CODES.keys()) + list(self.custom_colors.keys())

    @staticmethod
    def random_color():
        """
        Generates a random color code using ANSI escape sequence for text color manipulation.
        Returns the random color code as a string.
        """
        return (f'{Colorizer.CUSTOM_COLOR_PREFIX}'
                f'{random.randint(Colorizer.ALL_VALID_CODES_RANGE[0], Colorizer.ALL_VALID_CODES_RANGE[-1])}'
                f'{Colorizer.COLOR_SUFFIX}')

    def colorize(self, text, color=None, bold=False):
        """
        Method to colorize text with specified color and bold formatting if needed.

        Parameters:
        - text: str - the text to be colorized
        - color: str - the color to be applied, default is None
        - bold: bool - flag to determine if bold formatting should be applied, default is False

        Returns:
        - str: the colorized text
        """
        if not color:
            color_code = self.random_color()
        else:
            color_code = self.get_color_code(color)

        if bold:
            color_code = self.make_bold(color_code)
        return f"{color_code}{text}{Colorizer.RESET_COLOR_CODE}"

    def print_color(self, text, **kwargs):
        """
        A method to print colored text with optional formatting.

        Args:
            text (str): The text to be printed.
        Kwargs:
            color (str): Optional. The color of the text. Default is None.
            bold (bool): Optional. Whether the text should be bold. Default is False.
            extra_print_args (dict): Optional. Extra keyword arguments to be passed to the print function.

        Returns:
            None

        Raises:
            None
        """
        color = kwargs.get('color', None)
        bold = kwargs.get('bold', False)
        extra_print_args = kwargs.get('extra_print_args', {})

        print(self.colorize(text, color, bold), **extra_print_args)

    def preview_color_id(self, color_id: Union[int, Tuple[int, int, int]]):
        """
        Method to preview a specific color ID by printing it using the provided color ID.

        Parameters:
        - color_id (int): The ID of the color to preview.
        """
        self.print_color(str(color_id), color={color_id: color_id})

    def print_color_table(self, columns=21):
        """
        Prints a table of all valid color IDs with their corresponding color codes and attributes.
        The method takes an optional parameter columns which determines the number of columns in the table.
        It iterates through the range of valid color codes and prints each color ID along with its color
        and bold attribute.
        The table is formatted with the specified number of columns with the color IDs aligned properly.
        """
        counter = 0
        print(f' All Valid Color IDs '.center(columns * 5, '-'), end='\n\n')
        for x in Colorizer.ALL_VALID_CODES_RANGE:
            self.print_color(f'{x: >3}', color={x: x}, bold=True,
                             extra_print_args={'end': ' '})
            counter += 1
            if counter % columns == 0:
                print()

    @staticmethod
    def make_bold(color_code):
        """
        Static method to make a given color code bold.
        Takes a color code string as input and returns the same code with the bold formatting applied.
        """
        return color_code.replace('[', '[1;')

    def pretty_print_all_loaded_colors(self):
        """
        Method to print all available colors in a visually appealing way.

        Iterates through all loaded colors and prints each one with its colorized version.
        """
        print('All Available Colors: ')
        for color in self.all_loaded_colors:
            print(self.colorize(color, color))

    def example_usage(self):
        """
        A class that provides methods for printing colored text and displaying available colors.

        Methods:
        - print_color(text, color): Prints the given text in the specified color.
        - pretty_print_all_available_colors(): Prints all available colors for text formatting.
        """
        # Usage examples
        self.print_color("Warning: Low disk space", color="yellow")
        self.print_color("Error: Connection failed", color="red")
        self.print_color("Success: Test passed", color="green")
        print()
        self.pretty_print_all_loaded_colors()
        print()
        self.print_color_table()


class ColorConverter:
    RGB_LEVELS = [0, 95, 135, 175, 215, 255]
    GRAYSCALE_BRIGHTNESS_START = 8
    BRIGHTNESS_MULTIPLIER = 10
    BASIC_ANSI_RANGE = range(0, 16)
    RGB_RANGE = range(0, 232)
    GRAYSCALE_RANGE = range(232, 256)
    ANSI_16_TO_HEX = {
        30: "#000000",
        31: "#800000",
        32: "#008000",
        33: "#808000",
        34: "#000080",
        35: "#800080",
        36: "#008080",
        37: "#c0c0c0",
        90: "#808080",
        91: "#ff0000",
        92: "#00ff00",
        93: "#ffff00",
        94: "#0000ff",
        95: "#ff00ff",
        96: "#00ffff",
        97: "#ffffff",
    }

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

    @classmethod
    def to_tqdm_colour(cls, color: str) -> str:
        """
        Normalize a color value into something suitable for tqdm's colour argument.

        If given an ANSI escape sequence, it returns a hex color.
        If given an existing hex color or normal color name, it returns it unchanged.
        """
        bar_colors = []
        try:
            from tqdm.std import Bar
            bar_colors = Bar.COLOURS
        except ImportError:
            pass

        if not isinstance(color, str):
            raise TypeError(f"color must be a string, not {type(color)}")

        if "\033[" in color or "\x1b[" in color:
            return cls.ansi_escape_to_hex(color)
        elif not bar_colors:
            # TODO: add warning then raise below?
            ...

        elif color.upper() in bar_colors:
            return color.upper()
        else:
            raise InvalidColorInputError(f"Unsupported color: {color!r}")



if __name__ == "__main__":
    # test_custom_colors = {
    #     'dark_blue': Colorizer.CUSTOM_COLOR_PREFIX + '25m',
    #     'orange': (255, 150, 0),
    #     'pink': 211
    # }
    test_custom_colors = {}
    c = Colorizer(custom_colors=test_custom_colors, ignore_invalid_colors=False)
    c.example_usage()
