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
    """ Class for coloring text in the terminal with ANSI escape codes. """
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
        self.ignore_invalid_colors = kwargs.get('ignore_invalid_colors', False)
        self._custom_colors_populated = False
        self._custom_colors = custom_colors or {}

    @property
    def custom_colors(self):
        """
        Retrieve and format custom colors based on predefined rules.
        If custom colors have not been populated yet,
        iterate over the internal dictionary of custom colors.
        If the value of a custom color is an integer,
        convert it to the corresponding color code.
        If the value is a string starting with '\033', leave it as is.
        Update the temporary dictionary with the formatted color data.
        Finally, set the internal custom colors to the processed dictionary
        and mark custom colors as populated.
        Return the custom colors dictionary.
        """
        if not self._custom_colors_populated:
            temp_dict = {}
            for x in self._custom_colors.items():
                if isinstance(x[1], int):
                    x = {x[0].upper(): self.get_color_code({x[0]: x[1]})}
                elif isinstance(x[1], str) and x[1].startswith('\033'):
                    x = {x[0].upper(): x[1]}
                temp_dict.update(x)
            self._custom_colors = temp_dict
            self._custom_colors_populated = True

        return self._custom_colors

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
                f'{random.randint(Colorizer.ALL_VALID_CODES_RANGE[0],
                                  Colorizer.ALL_VALID_CODES_RANGE[-1])}m')

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

    def preview_color_id(self, color_id: int):
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
    def stringify_color_id(color_id: int):
        """
        This method converts a color ID to a string format for colorization.
         The color ID should be an integer value within the valid range specified by the Colorizer class.
         If the provided color ID is within the valid range, the method returns a string representation of the color ID.
          If the color ID is outside the valid range, an InvalidColorCode exception
          is raised indicating that the color ID must be an integer between 0 and 255.
        """
        if color_id in Colorizer.ALL_VALID_CODES_RANGE:
            return f'{Colorizer.CUSTOM_COLOR_PREFIX}{color_id}m'
        else:
            raise InvalidColorCode("color_id must be an integer between 0 and 255")

    def _parse_color_string(self, color_string: str):
        """
        Parses a color string and returns the corresponding color code.
        If the color string is not found in the default color codes dictionary or the custom colors dictionary,
        it returns an empty string.
        If the 'ignore_invalid_colors' flag is not set, it raises an InvalidColorCode exception.
        """
        full_str = Colorizer.DEFAULT_COLOR_CODES.get(color_string.upper(),
                                                     self.custom_colors.get(color_string.upper(), ''))
        if full_str != '':
            return full_str
        else:
            if not self.ignore_invalid_colors:
                raise InvalidColorCode('given color did not match any of the available colors')
            return full_str

    def get_color_code(self, color: Union[str, dict, int]) -> str:
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

        elif isinstance(color, str):
            return self._parse_color_string(color)
        else:
            raise AttributeError("color attribute must be a string or a dictionary")

    @staticmethod
    def make_bold(color_code):
        """
        Static method to make a given color code bold. Takes a color code string as input and returns the same code with the bold formatting applied.
        """
        return color_code.replace('[', '[1;')

    def pretty_print_all_available_colors(self):
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
        self.pretty_print_all_available_colors()

    @staticmethod
    def rgb_to_hex(rgb):
        """
        Convert RGB tuple to hexadecimal color representation.

        Args:
            rgb (tuple): RGB color tuple in the format (R, G, B) where each component is an integer between 0 and 255.

        Returns:
            str: Hexadecimal color representation.
        """
        return '#{0:02x}{1:02x}{2:02x}'.format(*rgb)

    @staticmethod
    def hex_to_rgb(hex_color):
        """
        Convert hexadecimal color representation to RGB tuple.

        Args:
            hex_color (str): Hexadecimal color representation (e.g., '#RRGGBB').

        Returns:
            tuple: RGB color tuple in the format (R, G, B) where each component is an integer between 0 and 255.
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    test_custom_colors = {
        'dark_blue': Colorizer.CUSTOM_COLOR_PREFIX + '25m',
        'light_pink': 210
    }
    c = Colorizer(custom_colors=test_custom_colors, ignore_invalid_colors=False)
    c.example_usage()
    #c.preview_color_id(25)
