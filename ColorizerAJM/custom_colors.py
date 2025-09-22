from json import dump, load
from pathlib import Path

from ColorizerAJM import _ColorizerInitializer


class CustomColorColorizer(_ColorizerInitializer):
    DEFAULT_CUSTOM_COLOR_FILE_PATH = Path('./custom_colors.json')

    def __init__(self, custom_colors: dict = None, **kwargs):
        super().__init__(**kwargs)
        self._custom_colors = None
        self.custom_colors = custom_colors or {}
        self.custom_color_file_path = kwargs.get('custom_color_file_path',
                                                 self.__class__.DEFAULT_CUSTOM_COLOR_FILE_PATH)
        if kwargs.get('write_custom_colors_on_init', True):
            self.write_custom_colors()

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
        return self._custom_colors

    @custom_colors.setter
    def custom_colors(self, value: dict):
        temp_dict = {}
        if self._custom_colors:
            temp_dict = self._custom_colors.copy()
        for x in value.items():
            if isinstance(x[1], int):
                x = {x[0].upper(): self.get_color_code({x[0]: x[1]})}
            elif isinstance(x[1], tuple) and len(x[1]) == 3:
                x = {x[0].upper(): self.get_color_code(x[1])}
            elif isinstance(x[1], str) and x[1].startswith('\033'):
                x = {x[0].upper(): x[1]}
            temp_dict.update(x)
        self._custom_colors = temp_dict

    def write_custom_colors(self):
        if self.custom_colors:
            with open(self.custom_color_file_path, 'w') as f:
                dump(self.custom_colors, fp=f, indent=4)

    def read_custom_colors(self):
        if self.custom_color_file_path.is_file() and self.custom_color_file_path.suffix == '.json':
            with open(self.custom_color_file_path, 'r') as f:
                self.custom_colors = load(f)
                print(f"custom colors loaded from {f.name}")
                # TODO: log here
        else:
            raise AttributeError(f"custom color file path is not a valid file or does not have a .json extension")
