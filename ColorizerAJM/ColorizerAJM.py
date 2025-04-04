"""
ColorizerAJM.py

Taken from https://medium.com/@ryan_forrester_/adding-color-to-python-terminal-output-a-complete-guide-147fcb1c335f uses ANSI escape codes to colorize terminal output

"""

from _version import __version__


class Colorizer:
    DEFAULT_COLOR_CODES = {
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'BLUE': '\033[94m',
        'YELLOW': '\033[93m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
    }
    RESET_COLOR = '\033[0m'

    def __init__(self, custom_colors: dict = None):
        """
        Uses ANSI escape codes to colorize terminal output

        :param custom_colors: A dictionary containing custom colors for the software.
        :type custom_colors: dict
        """
        self.custom_colors = custom_colors or {}

    @property
    def all_available_colors(self):
        return list(Colorizer.DEFAULT_COLOR_CODES.keys()) + list(self.custom_colors.keys())

    def colorize(self, text, color, bold=False):
        """Add color to text, first looking in the class dict DEFAULT_COLOR_CODES, then looking in the custom_colors dict,
         and handle reset automatically"""
        color_code = self.get_color_code(color)
        if bold:
            color_code = self.make_bold(color_code)
        return f"{color_code}{text}{Colorizer.RESET_COLOR}"

    def get_color_code(self, color: str) -> str:
        """Retrieve color code from default or custom colors."""
        return Colorizer.DEFAULT_COLOR_CODES.get(color.upper(), self.custom_colors.get(color.upper(), ''))

    @staticmethod
    def make_bold(color_code):
        return color_code.replace('[', '[1;')

    def example_usage(self):
        # Usage examples
        print(self.colorize("Warning: Low disk space", "yellow"))
        print(self.colorize("Error: Connection failed", "red"))
        print(self.colorize("Success: Test passed", "green"))


if __name__ == "__main__":
    c = Colorizer()
    print(c.all_available_colors)
    c.example_usage()