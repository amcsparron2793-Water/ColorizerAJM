"""
ColorizerAJM.py

adapted from https://medium.com/@ryan_forrester_/adding-color-to-python-terminal-output-a-complete-guide-147fcb1c335f

uses ANSI escape codes to colorize terminal output

"""
import random
from typing import Union


class InvalidColorCodeError(Exception):
    """Raised when an invalid color code is encountered."""
    ...


class MissingColorDefinitionError(Exception):
    """Raised when neither rgb nor hex is provided."""
    ...


class InvalidColorInputError(Exception):
    """Raised when invalid rgb or hex input is given."""
    ...

# TODO: add in background color functionality
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
    RGBA_COLOR_PREFIX = '\033[38;2;'
    COLOR_SUFFIX = 'm'
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
                elif isinstance(x[1], tuple) and len(x[1]) == 3:
                    x = {x[0].upper(): self.get_color_code(x[1])}
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
                                  Colorizer.ALL_VALID_CODES_RANGE[-1])}{Colorizer.COLOR_SUFFIX}')

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

    def preview_color_id(self, color_id: Union[int, tuple[int, int, int]]):
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
    def stringify_color_id(color_id: Union[int, tuple]):
        """ Converts a color ID (integer or RGB tuple) into a string format for colorization.
            - For an integer within the valid range (0-255), returns the ANSI escape code for the color.
            - For a tuple of 3 integers (each in the range 0-255), returns the RGB ANSI escape code.
            Raises:
                InvalidColorCodeError: If the input is not a valid color ID. """
        if isinstance(color_id, int):
            if color_id in Colorizer.ALL_VALID_CODES_RANGE:
                return f'{Colorizer.CUSTOM_COLOR_PREFIX}{color_id}{Colorizer.COLOR_SUFFIX}'
            else:
                raise InvalidColorCodeError("color_id must be an integer between 0 and 255")
        elif isinstance(color_id, tuple):
            if len(color_id) == 3 and all(c in Colorizer.ALL_VALID_CODES_RANGE for c in color_id):
                return f'{Colorizer.RGBA_COLOR_PREFIX}{color_id[0]};{color_id[1]};{color_id[2]}{Colorizer.COLOR_SUFFIX}'
            raise InvalidColorCodeError("color_id must be an integer OR a tuple of three integers between 0 and 255")

    def _parse_color_string(self, color_string: str):
        """
        Parses a color string and returns the corresponding color code.
        If the color string is not found in the default color codes dictionary or the custom colors dictionary,
        it returns an empty string.
        If the 'ignore_invalid_colors' flag is not set, it raises an InvalidColorCodeError exception.
        """
        full_str = Colorizer.DEFAULT_COLOR_CODES.get(color_string.upper(),
                                                     self.custom_colors.get(color_string.upper(), ''))
        if full_str != '':
            return full_str
        else:
            if not self.ignore_invalid_colors:
                raise InvalidColorCodeError('given color did not match any of the available colors')
            return full_str

    def get_color_code(self, color: Union[str, dict, int, tuple[int, int, int]]) -> str:
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

    @staticmethod
    def make_bold(color_code):
        """
        Static method to make a given color code bold. Takes a color code string as input and returns the same code with the bold formatting applied.
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
    """
    Allows converting between RGB and hexadecimal color representations.

    The constructor __init__ initializes the ColorConverter with either an RGB color tuple (rgb_color)
     or a hexadecimal color string (hex_color).
     It validates the input and ensures that only one of the color representations is provided.

    The method rgb_to_hex converts an RGB color tuple to a hexadecimal color representation.
    It takes a tuple of three integers between 0 and 255 representing the RGB components
    and returns a string in the format "#RRGGBB".

    The method hex_to_rgb converts a hexadecimal color representation to an RGB color tuple.
    It takes a string in the format "#RRGGBB" representing the color and returns a tuple
     of three integers between 0 and 255 representing the RGB components.
    """
    def __init__(self, rgb_color=None, hex_color=None):
        self.rgb_color = rgb_color
        self.hex_color = hex_color
        if not self.rgb_color and not self.hex_color:
            raise MissingColorDefinitionError('either rgb or hex must be provided')

        if self.rgb_color and self.hex_color:
            raise AttributeError('only one of rgb or hex can be provided')

        # Validate RGB input
        if self.rgb_color:
            if (
                    not isinstance(self.rgb_color, tuple)
                    or len(self.rgb_color) != 3
                    or any(not isinstance(c, int) or not (0 <= c <= 255) for c in self.rgb_color)
            ):
                raise InvalidColorInputError('RGB must be a tuple of three integers between 0 and 255')

        # Validate HEX input
        if self.hex_color:
            if not isinstance(self.hex_color, str) or not self.hex_color.startswith('#') or len(self.hex_color) != 7:
                raise InvalidColorInputError('Hex must be a string in the format "#RRGGBB"')
    
    def rgb_to_hex(self):
        """
        Convert RGB tuple to hexadecimal color representation.

        Args:
            rgb (tuple): RGB color tuple in the format (R, G, B) where each component is an integer between 0 and 255.

        Returns:
            str: Hexadecimal color representation.
        """
        if not self.rgb_color:
            raise InvalidColorInputError('RGB tuple is not provided')
        return '#{0:02x}{1:02x}{2:02x}'.format(*self.rgb_color)

    def hex_to_rgb(self):
        """
        Convert hexadecimal color representation to RGB tuple.

        Returns:
            tuple: RGB color tuple in the format (R, G, B) where each component is an integer between 0 and 255.
        """
        if not self.hex_color:
            raise InvalidColorInputError('Hexadecimal color representation is not provided')
        hex_color = self.hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    test_custom_colors = {
        'dark_blue': Colorizer.CUSTOM_COLOR_PREFIX + '25m',
        'orange': (255, 150, 0),
        'pink': 211
    }
    c = Colorizer(custom_colors=test_custom_colors, ignore_invalid_colors=False)
    c.example_usage()
